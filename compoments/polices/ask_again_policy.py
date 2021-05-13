import json
from typing import List, Optional, Text, Tuple, Dict, Any

from rasa.core.policies.rule_policy import RulePolicy, RULES, RULES_FOR_LOOP_UNHAPPY_PATH, DO_NOT_PREDICT_LOOP_ACTION, \
    logger, LOOP_RULES, LOOP_WAS_INTERRUPTED
from rasa.shared.core.constants import ACTION_LISTEN_NAME, PREVIOUS_ACTION, USER
from rasa.shared.nlu.constants import ACTION_NAME, INTENT, TEXT
from rasa.shared.core.domain import Domain, State
from rasa.shared.core.trackers import DialogueStateTracker, get_active_loop_name


class AskAgainRulePolicy(RulePolicy):
    def __init__(
        self,
        ask_again_intent=Optional[str],
        need_ask_again_intents=Optional[List[str]],
        **kwargs
    ):
        """

        :param ask_again_intent: ask again key intent
        :param need_ask_again_intents: need to ask again intents in rules
        :param kwargs:
        """
        super().__init__(**kwargs)
        self._ask_again_intent = ask_again_intent
        self._need_ask_again_intents = need_ask_again_intents
        if self.lookup.get(RULES) and ask_again_intent and need_ask_again_intents:
            self.update_rules()

    def _find_action_from_rules(
            self,
            tracker: DialogueStateTracker,
            domain: Domain,
            use_text_for_last_user_input: bool,
    ) -> Tuple[Optional[Text], Optional[Text], bool]:
        """Predicts the next action based on the memoized rules.

        Args:
            tracker: The current conversation tracker.
            domain: The domain of the current model.
            use_text_for_last_user_input: `True` if text of last user message
                should be used for the prediction. `False` if intent should be used.

        Returns:
            A tuple of the predicted action name or text (or `None` if no matching rule
            was found), a description of the matching rule, and `True` if a loop action
            was predicted after the loop has been in an unhappy path before.
        """
        if (
                use_text_for_last_user_input
                and not tracker.latest_action_name == ACTION_LISTEN_NAME
        ):
            # make text prediction only directly after user utterance
            # because we've otherwise already decided whether to use
            # the text or the intent
            return None, None, False

        tracker_as_states = self.featurizer.prediction_states(
            [tracker], domain, use_text_for_last_user_input
        )
        states = tracker_as_states[0]

        current_states = self.format_tracker_states(states)
        logger.debug(f"Current tracker state:{current_states}")

        # Tracks if we are returning after an unhappy loop path. If this becomes `True`
        # the policy returns an event which notifies the loop action that it
        # is returning after an unhappy path. For example, the `FormAction` uses this
        # to skip the validation of slots for its first execution after an unhappy path.
        returning_from_unhappy_path = False

        rule_keys = self._get_possible_keys(self.lookup[RULES], states)
        predicted_action_name = None
        best_rule_key = ""
        if rule_keys:
            # if there are several rules,
            # it should mean that some rule is a subset of another rule
            # therefore we pick a rule of maximum length
            best_rule_key = max(rule_keys, key=len)
            predicted_action_name = self.lookup[RULES].get(best_rule_key)

        active_loop_name = tracker.active_loop_name
        if active_loop_name:
            # find rules for unhappy path of the loop
            loop_unhappy_keys = self._get_possible_keys(
                self.lookup[RULES_FOR_LOOP_UNHAPPY_PATH], states
            )
            # there could be several unhappy path conditions
            unhappy_path_conditions = [
                self.lookup[RULES_FOR_LOOP_UNHAPPY_PATH].get(key)
                for key in loop_unhappy_keys
            ]

            # Check if a rule that predicted action_listen
            # was applied inside the loop.
            # Rules might not explicitly switch back to the loop.
            # Hence, we have to take care of that.
            predicted_listen_from_general_rule = (
                    predicted_action_name == ACTION_LISTEN_NAME
                    and not get_active_loop_name(self._rule_key_to_state(best_rule_key)[-1])
            )
            if predicted_listen_from_general_rule:
                if DO_NOT_PREDICT_LOOP_ACTION not in unhappy_path_conditions:
                    # negative rules don't contain a key that corresponds to
                    # the fact that active_loop shouldn't be predicted
                    logger.debug(
                        f"Predicted loop '{active_loop_name}' by overwriting "
                        f"'{ACTION_LISTEN_NAME}' predicted by general rule."
                    )
                    return active_loop_name, LOOP_RULES, returning_from_unhappy_path

                # do not predict anything
                predicted_action_name = None

            if LOOP_WAS_INTERRUPTED in unhappy_path_conditions:
                logger.debug(
                    "Returning from unhappy path. Loop will be notified that "
                    "it was interrupted."
                )
                returning_from_unhappy_path = True

        if predicted_action_name is not None:
            logger.debug(
                f"There is a rule for the next action '{predicted_action_name}'."
            )
        else:
            logger.debug("There is no applicable rule.")

        # if we didn't predict anything from the rules, then the feature key created
        # from states can be used as an indicator that this state will lead to fallback
        return (
            predicted_action_name or self.get_again_action_from_states(states),
            best_rule_key or self._create_feature_key(states),
            returning_from_unhappy_path,
        )

    def get_again_action_from_states(self, states: List[State]) -> Optional[Text]:
        latest_user_state = states[-1].get(USER, {})
        if self.states_is_ask_again_intent(latest_user_state):
            return self.get_latest_ask_again_action(states)
        return None

    def states_is_ask_again_intent(self, user_state: Dict[str, str]) -> bool:
        """看 intent 是否是设置的 intent """
        return (not user_state.get(TEXT)) and (user_state.get(INTENT, "") == self._ask_again_intent)

    def get_latest_ask_again_action(self, states: List[State]) -> Optional[str]:
        """获取上一次的 action name"""
        for state in states[-2:0:-2]:
            intent = state[USER][INTENT]
            if intent in self._need_ask_again_intents:
                return state[PREVIOUS_ACTION][ACTION_NAME]
            elif intent == self._ask_again_intent:
                continue
            else:
                return None
        return None

    def _metadata(self) -> Dict[Text, Any]:

        return {
            "priority": self.priority,
            "lookup": self.lookup,
            "core_fallback_threshold": self._core_fallback_threshold,
            "core_fallback_action_name": self._fallback_action_name,
            "enable_fallback_prediction": self._enable_fallback_prediction,
            "ask_again_intent": self._ask_again_intent,
            "need_ask_again_intents": self._need_ask_again_intents
        }

    @classmethod
    def _metadata_filename(cls) -> Text:
        return "ask_again_rule_policy.json"

    def update_rules(self) -> None:
        """根据 指定参数来更新 rules"""
        tmp_rules = {}
        for intent in self._need_ask_again_intents:
            action_name = self.get_action_name_by_intent(intent)
            tmp_rules[self._get_action_dumps_string_for_rule(action_name)] = ACTION_LISTEN_NAME
        self.lookup[RULES].update(tmp_rules)

    def get_action_name_by_intent(self, intent: str) -> Optional[str]:
        return self.lookup[RULES].get(self._generate_dumps_string(intent))

    @staticmethod
    def _generate_dumps_string(intent: str) -> str:
        return json.dumps([{PREVIOUS_ACTION: {ACTION_NAME: ACTION_LISTEN_NAME}, USER: {INTENT: intent}}])

    def _get_action_dumps_string_for_rule(self, action_name: str) -> str:
        return json.dumps(
            [{PREVIOUS_ACTION: {ACTION_NAME: ACTION_LISTEN_NAME}, USER: {INTENT: self._ask_again_intent}},
             {PREVIOUS_ACTION: {ACTION_NAME: action_name},
              USER: {INTENT: self._ask_again_intent}}])


if __name__ == '__main__':
    # print(common.arguments_of(AskAgainRulePolicy.__init__))
    res = {
        "[{\"prev_action\": {\"action_name\": \"action_listen\"}, \"user\": {\"intent\": \"rasa_faq\"}}]": "utter_rasa_faq",
        "[{\"prev_action\": {\"action_name\": \"action_listen\"}, \"user\": {\"intent\": \"rasa_faq\"}}, {\"prev_action\": {\"action_name\": \"utter_rasa_faq\"}, \"user\": {\"intent\": \"rasa_faq\"}}]": "action_listen",
        "[{\"prev_action\": {\"action_name\": \"action_listen\"}, \"user\": {\"intent\": \"\\u67e5\\u8be2\\u65f6\\u95f4\"}}]": "action_query_time",
        "[{\"prev_action\": {\"action_name\": \"action_listen\"}, \"user\": {\"intent\": \"\\u67e5\\u8be2\\u65f6\\u95f4\"}}, {\"prev_action\": {\"action_name\": \"action_query_time\"}, \"user\": {\"intent\": \"\\u67e5\\u8be2\\u65f6\\u95f4\"}}]": "action_listen",
        "[{\"prev_action\": {\"action_name\": \"action_listen\"}, \"user\": {\"intent\": \"bot_challenge\"}}]": "utter_iamabot",
        "[{\"prev_action\": {\"action_name\": \"action_listen\"}, \"user\": {\"intent\": \"bot_challenge\"}}, {\"prev_action\": {\"action_name\": \"utter_iamabot\"}, \"user\": {\"intent\": \"bot_challenge\"}}]": "action_listen",
        "[{\"prev_action\": {\"action_name\": \"action_listen\"}, \"user\": {\"intent\": \"goodbye\"}}]": "utter_goodbye",
        "[{\"prev_action\": {\"action_name\": \"action_listen\"}, \"user\": {\"intent\": \"goodbye\"}}, {\"prev_action\": {\"action_name\": \"utter_goodbye\"}, \"user\": {\"intent\": \"goodbye\"}}]": "action_listen",
        "[{\"prev_action\": {\"action_name\": \"action_listen\"}, \"user\": {\"intent\": \"\\u67e5\\u8be2\\u5929\\u6c14\"}}]": "action_query_weather",
        "[{\"prev_action\": {\"action_name\": \"action_listen\"}, \"user\": {\"intent\": \"\\u67e5\\u8be2\\u5929\\u6c14\"}}, {\"prev_action\": {\"action_name\": \"action_query_weather\"}, \"user\": {\"intent\": \"\\u67e5\\u8be2\\u5929\\u6c14\"}}]": "action_listen"
    }

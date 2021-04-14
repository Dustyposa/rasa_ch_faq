import json
from typing import List, Optional, Text, Tuple, Dict, Any

from rasa.core.policies.rule_policy import RulePolicy, RULES, RULES_FOR_LOOP_UNHAPPY_PATH, DO_NOT_PREDICT_LOOP_ACTION, \
    logger, LOOP_RULES, LOOP_WAS_INTERRUPTED
from rasa.shared.core.constants import ACTION_LISTEN_NAME, PREVIOUS_ACTION, USER
from rasa.shared.nlu.constants import ACTION_NAME, INTENT, TEXT
from rasa.shared.core.domain import Domain, State
from rasa.shared.core.trackers import DialogueStateTracker, get_active_loop_name
from rasa.shared.utils import common


class AskAgainRulePolicy(RulePolicy):
    def __init__(self, ask_again_intent=None, need_ask_again_intents=None, **kwargs):
        super().__init__(**kwargs)
        self._ask_again_intent = ask_again_intent
        self._need_ask_again_intents = need_ask_again_intents
        if self.lookup.get(RULES) and self._ask_again_intent and self._need_ask_again_intents:
            self.lookup[RULES].update({
                json.dumps(
                    [{PREVIOUS_ACTION: {ACTION_NAME: ACTION_LISTEN_NAME}, USER: {INTENT: self._ask_again_intent}},
                     {PREVIOUS_ACTION: {ACTION_NAME: "action_query_weather"},
                      USER: {INTENT: self._ask_again_intent}}]): ACTION_LISTEN_NAME
            })

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
        latest_state = states[-1][USER]
        if (not latest_state.get(TEXT)) and (latest_state.get(INTENT, "").startswith(self._ask_again_intent)):
            prev_action_name = states[-2][PREVIOUS_ACTION][ACTION_NAME]
            if prev_action_name.startswith("action_query"):
                return prev_action_name
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


if __name__ == '__main__':
    print(common.arguments_of(AskAgainRulePolicy.__init__))

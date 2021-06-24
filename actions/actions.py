from typing import Text, Dict, Any, List, Optional

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase

from rasa_sdk.knowledge_base.utils import (SLOT_OBJECT_TYPE,
                                           SLOT_LAST_OBJECT_TYPE,
                                           SLOT_ATTRIBUTE,
                                           reset_attribute_slots,
                                           get_object_name,
                                           SLOT_MENTION,
                                           SLOT_LAST_OBJECT,
                                           SLOT_LISTED_OBJECTS)
from rasa_sdk.types import DomainDict
from rasa_sdk import utils

from actions.storage import Neo4JKnowledgeBase


def get_attribute_slots(
        tracker: "Tracker", object_attributes: List[Text]
) -> List[Dict[Text, Text]]:
    """
    Copied from rasa_sdk.knowledge_base.utils  and overridden
    as we also need to return the entity role for range queries.
    If the user mentioned one or multiple attributes of the provided object_type in
    an utterance, we extract all attribute values from the tracker and put them
    in a list. The list is used later on to filter a list of objects.
    For example: The user says 'What Italian restaurants do you know?'.
    The NER should detect 'Italian' as 'cuisine'.
    We know that 'cuisine' is an attribute of the object type 'restaurant'.
    Thus, this method returns [{'name': 'cuisine', 'value': 'Italian'}] as
    list of attributes for the object type 'restaurant'.
    Args:
        tracker: the tracker
        object_attributes: list of potential attributes of object
    Returns: a list of attributes
    """
    attributes = []

    for attr in object_attributes:
        attr_val = tracker.get_slot(attr) if attr in tracker.slots else None
        if attr_val is not None:
            entities = tracker.latest_message.get("entities", [])
            role = [e['role'] for e in entities if e['entity'] == attr and e['value'] == attr_val and 'role' in e]
            role = role[0] if len(role) else None
            attributes.append({"name": attr, "value": attr_val, "role": role})

    return attributes


def get_latest_entity_relation_role_value(tracker: Tracker) -> Optional[Text]:
    entities = tracker.latest_message.get("entities", [])
    for x in entities:
        if x.get("value") == "relation":
            return x.get("role")


class ActionNeo4JKB(ActionQueryKnowledgeBase):
    def __init__(self):
        # load knowledge base with data from the given file
        knowledge_base = Neo4JKnowledgeBase()

        # overwrite the representation function of the hotel object
        # by default the representation function is just the name of the object
        # knowledge_base.set_representation_function_of_object(
        #     "hotel", lambda obj: obj["name"] + " (" + obj["city"] + ")"
        # )

        super().__init__(knowledge_base)

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        object_type = tracker.get_slot(SLOT_OBJECT_TYPE)
        last_object_type = tracker.get_slot(SLOT_LAST_OBJECT_TYPE)
        attribute = tracker.get_slot(SLOT_ATTRIBUTE)

        new_request = object_type != last_object_type

        if not object_type:
            # object type always needs to be set as this is needed to query the
            # knowledge base
            dispatcher.utter_message(template="utter_ask_rephrase")
            return []

        if not attribute or new_request:
            return await self._query_objects(dispatcher, object_type, tracker)
        elif attribute:
            return await self._query_attribute(
                dispatcher, object_type, attribute, tracker
            )

        dispatcher.utter_message(template="utter_ask_rephrase")
        return []

    async def _query_objects(
            self, dispatcher: CollectingDispatcher, object_type: Text, tracker: Tracker
    ) -> List[Dict]:
        """
        Queries the knowledge base for objects of the requested object type and
        outputs those to the user. The objects are filtered by any attribute the
        user mentioned in the request.

        Args:
            dispatcher: the dispatcher
            tracker: the tracker

        Returns: list of slots
        """
        object_attributes = await utils.call_potential_coroutine(
            self.knowledge_base.get_attributes_of_object(object_type)
        )

        # get all set attribute slots of the object type to be able to filter the
        # list of objects
        attributes = get_attribute_slots(tracker, object_attributes)
        # query relation
        self._query_relations(tracker, attributes)
        # query the knowledge base
        objects = await utils.call_potential_coroutine(
            self.knowledge_base.get_objects(object_type, attributes)
        )

        await utils.call_potential_coroutine(
            self.utter_objects(dispatcher, object_type, objects)
        )

        if not objects:
            return reset_attribute_slots(tracker, object_attributes)

        key_attribute = await utils.call_potential_coroutine(
            self.knowledge_base.get_key_attribute_of_object(object_type)
        )

        last_object = None if len(objects) > 1 else objects[0][key_attribute]

        slots = [
            SlotSet(SLOT_OBJECT_TYPE, object_type),
            SlotSet(SLOT_MENTION, None),
            SlotSet(SLOT_ATTRIBUTE, None),
            SlotSet(SLOT_LAST_OBJECT, last_object),
            SlotSet(SLOT_LAST_OBJECT_TYPE, object_type),
            SlotSet(
                SLOT_LISTED_OBJECTS, list(map(lambda e: e[key_attribute], objects))
            ),
        ]

        return slots + reset_attribute_slots(tracker, object_attributes)

    def _query_relations(self, tracker: Tracker, attr: List) -> None:
        """关系查询"""

        for relation_key in (set(self.knowledge_base.relations) & tracker.slots.keys()):
            if tracker.get_slot(relation_key) \
                    and \
                    tracker.get_latest_entity_values(relation_key, entity_role="relation"):
                attr.append({"name": relation_key, "value": tracker.get_slot(relation_key), "role": "relation"})
                return

    async def _query_attribute(
            self,
            dispatcher: CollectingDispatcher,
            object_type: Text,
            attribute: Text,
            tracker: Tracker,
    ) -> List[Dict]:
        """
        Queries the knowledge base for the value of the requested attribute of the
        mentioned object and outputs it to the user.

        Args:
            dispatcher: the dispatcher
            tracker: the tracker

        Returns: list of slots
        """

        object_name = get_object_name(
            tracker,
            self.knowledge_base.ordinal_mention_mapping,
            self.use_last_object_mention,
        )
        if attribute == "relation":
            object_of_interest = await utils.call_potential_coroutine(
                self.knowledge_base.get_relation_object(
                    object_type, object_name, get_latest_entity_relation_role_value(tracker)
                )
            )

        elif not object_name or not attribute:
            dispatcher.utter_message(template="utter_ask_rephrase")
            return [SlotSet(SLOT_MENTION, None)]

        else:
            object_of_interest = await utils.call_potential_coroutine(
                self.knowledge_base.get_object(object_type, object_name)
            )

        if not object_of_interest or attribute not in object_of_interest:
            dispatcher.utter_message(template="utter_ask_rephrase")
            return [SlotSet(SLOT_MENTION, None)]

        value = object_of_interest[attribute]

        object_representation = (await utils.call_potential_coroutine(
            self.knowledge_base.get_representation_function_of_object(object_type)
        ))(object_of_interest)

        key_attribute = await utils.call_potential_coroutine(
            self.knowledge_base.get_key_attribute_of_object(object_type)
        )

        object_identifier = object_of_interest[key_attribute]

        await utils.call_potential_coroutine(
            self.utter_attribute_value(
                dispatcher, object_representation, attribute, value
            )
        )

        slots = [
            SlotSet(SLOT_OBJECT_TYPE, object_type),
            SlotSet(SLOT_ATTRIBUTE, None),
            SlotSet(SLOT_MENTION, None),
            SlotSet(SLOT_LAST_OBJECT, object_identifier),
            SlotSet(SLOT_LAST_OBJECT_TYPE, object_type),
        ]

        return slots

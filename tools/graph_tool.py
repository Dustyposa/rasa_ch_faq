from enum import Enum
from itertools import chain
from typing import Text, Dict, Any, List

from rasa_sdk.knowledge_base.storage import KnowledgeBase


class CypherEnum(str, Enum):
    get_all_labels = "MATCH (n) RETURN distinct labels(n)"
    get_node = "MATCH (p:{}) RETURN p LIMIT 1"


class Neo4JKnowledgeBase(KnowledgeBase):

    def __init__(self):
        self.graph = ...
        self.data = self.get_data()
        super().__init__()

    async def get_object(
            self, object_type: Text, object_identifier: Text
    ) -> Dict[Text, Any]:
        ...

    async def get_objects(
            self, object_type: Text, attributes: List[Dict[Text, Text]], limit: int = 5
    ) -> List[Dict[Text, Any]]:
        if object_type not in self.data:
            return []
        # filter objects by attributes
        cypher = "MATCH p: {0}\n"

        if attributes:
            cypher += "WHERE " + "AND".join([f"p.{a['name']}=={a['value']}" for a in attributes]) + "\n"
        cypher += f"RETURN p LIMIT {limit}"
        return self.run_graph(cypher).to_series().to_list()

    def get_attributes_of_object(self, object_type: Text) -> List[Text]:
        """
        Args:
            object_type:

        Returns: 所有的 node 的 property

        """
        return list(self.run_graph(CypherEnum.get_node.format(object_type)).to_series()[0].keys())

    def run_graph(self, cypher: str):
        return self.graph.run(cypher)

    def get_data(self):
        """
        获取所有的 labels
        Returns:

        """
        return list(chain.from_iterable(self.run_graph(CypherEnum.get_all_labels).to_series()))

from collections import defaultdict
from enum import Enum
from itertools import chain
from typing import Text, Dict, Any, List, Optional, Callable

from actions.queres import generate_list_query
from rasa_sdk.knowledge_base.storage import KnowledgeBase, InMemoryKnowledgeBase

QUERY_GENERATE_TABLE: Dict[str, Callable] = defaultdict(lambda: lambda k, v: f"{k}=\"{v}\"")

QUERY_GENERATE_TABLE.update(**{
    "language": generate_list_query,
    "category": generate_list_query,
})


class CypherEnum(str, Enum):
    get_all_labels = "MATCH (n) RETURN distinct labels(n)"
    get_node = "MATCH (p:{0}) RETURN p LIMIT 1"
    get_object_by_id = "MATCH (p:{0}) WHERE p.id=\"{1}\" RETURN p"
    get_object_by_and_relation = "MATCH " \
                                 "(o:{object_type}{{id:\"{obj_id}\"}}) -[{relation}] -> (r:{r_object_type}) RETURN r, o"


class Neo4JKnowledgeBase(KnowledgeBase):
    RELATION_TABLE = {
        "actor": ("Person", "name")
    }
    OBJ_RELATION_TABLE = {
        ("Movie", "actor"): "Person"
    }

    def __init__(self):
        from py2neo import Graph
        from actions.configs import NEO_ADDRESS
        self.graph = Graph(NEO_ADDRESS)
        # self.graph = ...
        self.relations = self._get_relations()
        self.data = self.get_data()
        super().__init__()
        self.representation_function.update(
            {
                "Movie": lambda obj: obj["title"],
                "Person": lambda obj: obj["name"],
            }
        )

    async def get_object(
            self, object_type: Text, object_identifier: Text
    ) -> Optional[Dict[Text, Any]]:
        if object_type not in self.data:
            return None

        obj_result = self.run_graph(CypherEnum.get_object_by_id.format(object_type, object_identifier)).to_series()
        return obj_result[0] if not obj_result.empty else None

    async def get_relation_object(
            self, object_type: Text, object_identifier: Text, relation: Text
    ) -> Optional[Dict[Text, Any]]:
        if self.OBJ_RELATION_TABLE.get((object_type, relation)) is None:
            return None
        search_dict = {
            "object_type": object_type,
            "obj_id": object_identifier,
            "relation": relation,
            "r_object_type": self.OBJ_RELATION_TABLE[(object_type, relation)]
        }
        res = self.run_graph(
            CypherEnum.get_object_by_and_relation.format(**search_dict)).to_data_frame()
        if not res.get("r").empty:
            r = res.loc[0, "o"]
            r["relation"] = list(map(lambda x: x["name"], res["r"].to_list()))
            return r

    async def get_objects(
            self, object_type: Text, attributes: List[Dict[Text, Text]], limit: int = 5
    ) -> List[Dict[Text, Any]]:
        if object_type not in self.data:
            return []
        if attributes and attributes[-1].get("role") == "relation":
            cypher = self.match_obj(object_type=object_type, relation_tuple=attributes.pop())
        else:
            cypher = f"MATCH (p: {object_type})\n"

        # filter objects by attributes
        if attributes:
            cypher += "WHERE " + " AND ".join(
                [QUERY_GENERATE_TABLE[a['name']](f"p.{a['name']}", a['value']) for a in attributes]) + "\n"
        cypher += f"RETURN p LIMIT {limit}"
        return self.run_graph(cypher).to_series().to_list()

    def get_attributes_of_object(self, object_type: Text) -> List[Text]:
        """
        Args:
            object_type:

        Returns: 所有的 node 的 property

        """
        return list(self.run_graph(CypherEnum.get_node.format(object_type.title())).to_series()[0].keys())

    def run_graph(self, cypher: str):
        print(F"cypher：{cypher}")

        return self.graph.run(cypher)

    def get_data(self):
        """
        获取所有的 labels
        Returns:

        """
        return list(chain.from_iterable(self.run_graph(CypherEnum.get_all_labels).to_series()))

    def _get_relations(self) -> List[str]:
        return self.run_graph(
            """MATCH ()-[relationship]->() 
RETURN TYPE(relationship) AS type, COUNT(relationship) AS amount
ORDER BY amount DESC;"""
        ).to_series().to_list()

    @classmethod
    def match_obj(cls, object_type: str, relation_tuple: Dict[str, str]) -> str:
        if relation_tuple and cls.RELATION_TABLE.get(relation_tuple["name"]):
            k, v = relation_tuple["name"], relation_tuple["value"]
            search_node, search_attr = cls.RELATION_TABLE[k]
            return f"""MATCH (p:Movie) - [:{k}] -> (:{search_node}{{{search_attr}: "{v}"}})\n"""
        return object_type

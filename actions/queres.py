from typing import Any, Dict


def generate_list_query(attribute: Dict[str, Any]) -> str:
    k, v = f"{attribute['name']}", attribute['value']
    return f"\"{v}\" in p.{k}"


def generate_range_query(attribute: Dict[str, Any]) -> str:
    k, v = f"{attribute['name']}", attribute['value']
    # 数据集未处理，自己特殊处理一下
    print(f"KV:{k}, {v}")
    if k == "showtime":
        v = f"{v}.0"
    role = attribute["role"]
    if role == "eq":
        operator = "="
    elif role == "lt":
        operator = "<"
    else:
        operator = ">"
    return f"p.{k} {operator} \"{v}\""

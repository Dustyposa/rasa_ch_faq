import asyncio

import yaml
from rasa.core.agent import Agent
from rasa.shared.constants import DEFAULT_ENDPOINTS_PATH
from rasa.utils.endpoints import EndpointConfig

# 需要先训练好一个模型
with open(DEFAULT_ENDPOINTS_PATH) as fp:
    endpoint = EndpointConfig.from_dict(yaml.load(fp).get("action_endpoint"))

agent = Agent.load_local_model(
    model_path="models",
    action_endpoint=endpoint
)

print(asyncio.run(agent.handle_text("rasax")))
print(asyncio.run(agent.handle_text("你是机器人吗？")))
print(asyncio.run(agent.handle_text("成都天气好吗？")))




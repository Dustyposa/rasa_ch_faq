import asyncio

from rasa.core.agent import Agent


# 需要先训练好一个模型
agent = Agent.load_local_model(
    model_path="models",
)

print(asyncio.run(agent.handle_text("rasax")))
print(asyncio.run(agent.handle_text("你是机器人吗？")))
print(asyncio.run(agent.handle_text("成都天气好吗？")))




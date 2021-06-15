FROM rasa/rasa:2.6.0
# 这是最小镜像，和自己的需要的lib依赖有关系，需要问题时可以参考注释部分。
# USER root  # 权限不足时打开

COPY . /app
WORKDIR /app
#RUN apt-get install -y gcc # 有gcc缺失时可以打开
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

ENTRYPOINT ["rasa"]
CMD ["run", "--cors", "*"]





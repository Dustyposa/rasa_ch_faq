FROM rasa/rasa:2.6.0

COPY . /app
WORKDIR /app
#RUN apt-get install -y gcc # 有gcc缺失时可以打开
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

ENTRYPOINT ["rasa"]
CMD ["run", "--cors", "*"]





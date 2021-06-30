![](https://img.shields.io/badge/python-3.7%20%7C%20-blue)
##  一个基于知识图谱的电影查询的对话机器人

### 待增加功能
- 1. 根据时间进行查询 


### 对话示例
[![RQE8gA.gif](https://z3.ax1x.com/2021/06/24/RQE8gA.gif)](https://imgtu.com/i/RQE8gA)

### 参考资料
#### 数据来源
> https://github.com/Linusp/kg-example
> 数据如何使用,[戳这里](https://www.zmonster.me/2019/04/30/neo4j-introduction.html#org02654fb)

#### 实现原理
[https://rasa.com/docs/action-server/knowledge-bases](https://rasa.com/docs/action-server/knowledge-bases)
> 参考实现:
> - [ES接入](https://medium.com/bakdata/conversational-search-in-knowledge-bases-using-nlp-nlu-and-chatbots-d84f74c09396)
 
### 如何使用

#### 1. 数据导入
- 脚本导入
> 看[这里](https://github.com/Dustyposa/kg-example)

- `Cypher` 命令行导入
    1. 创建 `Movie` 实体
    ```cypher
    LOAD CSV with headers from 'https://raw.githubusercontent.com/Linusp/kg-example/master/movie/Movie.csv' as line
    CREATE (:Movie {
           id:line["id:ID"],
           title:line["title"],
           url:line["url"],
           cover:line["cover"],
           rate:line["rate"],
           category:split(line["category:String[]"], ";"),
           language:split(line["language:String[]"], ";"),
           showtime:line["showtime"],
           length:line["length"],
           othername:split(line["othername:String[]"], ";")
           })
    ```
    2. 创建 `Person` 实体
    ```cypher
    LOAD CSV with headers from 'https://raw.githubusercontent.com/Linusp/kg-example/master/movie/Person.csv' as line
    CREATE (:Person {id:line["id:ID"], name:line["name"]})
    ```
   3. 创建 `Country` 实体
    ```cypher
        LOAD CSV with headers from 'https://raw.githubusercontent.com/Linusp/kg-example/master/movie/Country.csv' as line
    CREATE (:Country {id:line["id:ID"], name:line["name"]})
    ```
    1. 为实体创建索引（可跳过
    逐条执行
        ```cypher
        CREATE INDEX FOR (n:Movie) ON (n.id)
        CREATE INDEX FOR (n:Person) ON (n.id)
        CREATE INDEX FOR (n:Country) ON (n.id)
        ```
5. 加载关系
    `actor` 的关系
    ```cypher
    LOAD CSV with headers from 'https://raw.githubusercontent.com/Linusp/kg-example/master/movie/actor.csv' as line
    MATCH (a:Movie {id:line[":START_ID"]})
    MATCH (b:Person {id:line[":END_ID"]})
    CREATE (a)-[:actor]->(b)
    ```

    `composer` 的关系
    ```cypher
    LOAD CSV with headers from 'https://raw.githubusercontent.com/Linusp/kg-example/master/movie/composer.csv' as line
    MATCH (a:Movie {id:line[":START_ID"]})
    MATCH (b:Person {id:line[":END_ID"]})
    CREATE (a)-[:composer]->(b)
    ```
    `director` 的关系
    ```cypher
      LOAD CSV with headers from 'https://raw.githubusercontent.com/Linusp/kg-example/master/movie/director.csv' as line
    MATCH (a:Movie {id:line[":START_ID"]})
    MATCH (b:Person {id:line[":END_ID"]})
    CREATE (a)-[:director]->(b)
    ```
    `district` 的关系
    ```cypher
        LOAD CSV with headers from 'https://raw.githubusercontent.com/Linusp/kg-example/master/movie/district.csv' as line
    MATCH (a:Movie {id:line[":START_ID"]})
    MATCH (b:Country {id:line[":END_ID"]})
    CREATE (a)-[:district]->(b)
    ```
#### 2. 安装依赖以及训练

```bash
pip install -r requirements.txt && rasa train
```
#### 3. 更改 neo4j 的地址
在[这里](./actions/configs.py)
更改为数据库 ip 就行 

#### 4. 运行 rasa
主服务:
```bash
rasa run
```
`action` 服务
```bash
rasa run actions
```



### 一些问题解答

```
Q: 如何接入ES？
A: 可以参考这里 https://medium.com/bakdata/conversational-search-in-knowledge-bases-using-nlp-nlu-and-chatbots-d84f74c09396
``` 

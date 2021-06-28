![](https://img.shields.io/badge/python-3.7%20%7C%20-blue)
##  一个基于知识图谱的电影查询的对话机器人

### 待增加功能
- 暂无，有需求可以提 `issue` 哈


### 对话示例
新增时间段查询，eg：
```
Your input ->  能推荐一些2012年的电影吗？
Your input ->  能推荐一些2012年之后的电影吗？
```

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
- 1. 创建 `Movie` 实体
   


### 一些问题解答

```
Q: 如何接入ES？
A: 可以参考这里 https://medium.com/bakdata/conversational-search-in-knowledge-bases-using-nlp-nlu-and-chatbots-d84f74c09396
``` 

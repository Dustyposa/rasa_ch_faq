# rasa_ch_faq
用 `RASA` 实现 `RASA FAQ`。 回答关于 `RASA` 的问题。

![](https://img.shields.io/badge/python-3.7%20%7C%20-blue)

欢迎大家多提 `RASA` 相关的问题，我会补充在这里。
#### 功能更新
[2021-04-13] 实现追问demo，[实现细节](./piplines/)。

## 支持的问题列表
请参见: [问题列举](./data/nlu/rasa_faq.yml)

## 一些配置
分词使用的 `bert`， 自定义了 [`tokenizers`](./piplines/tokenizers.py) 

## 如何运行
由于使用了 `bert_chinese`， 所以 需要下载 `bert_chinese` 模型。
并放到 `pre_models` 文件夹中，重命名为 `tf_model.h5`
命令执行:
```bash
curl -L https://mirror.tuna.tsinghua.edu.cn/hugging-face-models/bert-base-chinese-tf_model.h5 -o pre_models/tf_model.h5
rasa train
``` 

## 运行示例
普通 `FAQ`:
![image.png](https://i.loli.net/2021/01/25/WndRk2ahfeI4i38.png)

追问：
![image.png](https://i.loli.net/2021/04/13/jr5lsAt728c3XCF.png)

### 一些文件说明
```
run.py  # 相当于运行 rasa run
train.py  # == rasa train
run_action_server.py  # == rasa run actions
```
### 一些工具
```bash
back_translation.py  # 回译脚本
# 使用方式
python back_translation.py 需要回译的文本
```

#### [我要直接看答案！！！](./data/nlu/responses/responses.yml)

# rasa_ch_faq
用 `RASA` 实现 `RASA FAQ`。 回答关于 `RASA` 的问题。

欢迎大家多提 `RASA` 相关的问题，我会补充在这里。


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
![image.png](https://i.loli.net/2021/01/25/WndRk2ahfeI4i38.png)


### 一些文件说明
```
run.py  # 相当于运行 rasa run
train.py  # == rasa train
```

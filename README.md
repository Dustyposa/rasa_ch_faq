![](https://img.shields.io/badge/python-3.7%20%7C%20-blue)


# rasa_ch_faq
用 `RASA` 实现 `RASA FAQ`。 回答关于 `RASA` 的问题。以及一些例子。


欢迎大家多提 `RASA` 相关的问题，我会补充在这里。
#### 功能更新
[2021-04-13] 实现追问demo，[实现细节](./compoments/polices)。

## 支持的问题列表
请参见: [问题列举](./data/nlu/rasa_faq.yml)

## 一些配置
分词使用的 `bert`， 自定义了 [`tokenizers`](./compoments/tokenizers/bert_tokenizer..py) 

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
load_model.py   # 直接加载并运行模型，与 server 无关。（需要先训练好一个模型） 
```
### 一些工具
```bash
back_translation.py  # 回译脚本
# 使用方式
python back_translation.py 需要回译的文本
```

#### [我要直接看答案！！！](./data/nlu/responses/responses.yml)

### 从零开始搭建机器人 
#### 1. 下载项目并进入
```bash
git clone https://github.com/Dustyposa/rasa_ch_faq.git 
cd rasa_ch_faq
```
#### 2. 安装依赖
```bash
pip install -r requirements.txt
curl -L https://mirror.tuna.tsinghua.edu.cn/hugging-face-models/bert-base-chinese-tf_model.h5 -o pre_models/tf_model.h5
rasa train
```
ps: 注意 `python` 版本 `37+`
#### 3. 训练模型
```bash
rasa train
```
#### 4. 运行机器人
需要开两个 `shell/iterm`
第一个:
```bash
rasa shell
```
第二个:
```bash
rasa run actions
```
然后就可以在第一个 `shell` 窗口对话了

### 从 1 开始搭建机器人
这个是干啥的?如果第一个你已经会了，我们加点前端展示的，效果康康这里:
![image.png](https://i.loli.net/2021/04/22/ofyR5w4MW9DGa7U.png)

#### 1. 下载前端项目并进入
```bash
git clone --depth 1 https://github.com/Dustyposa/ChatbotWidget.git
cd ChatbotWidget
```
#### 2. 运行 `index.html`
这个文件:
![image.png](https://i.loli.net/2021/04/22/uTicLEMs6rvXPnb.png)
#### 3. 启动 rasa
同样是两个 `shell/iterm`，第一个命令稍有不同:
```bash
rasa run --cors "*"
```
第二个:
```bash
rasa run actions
```
#### 4.开始对话
点它！开始对话:
![image.png](https://i.loli.net/2021/04/22/w4omyj8AUTHFLek.png)





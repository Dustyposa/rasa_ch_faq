## 一些工具
- [文本纠错](#文本纠错)

### 文本纠错
#### 如何开启
1. 下载模型，[模型地址](https://github.com/SeanLee97/xmnlp#%E4%B8%8B%E8%BD%BD%E5%9C%B0%E5%9D%80)
2. 设置 config
    ```yaml
    pipeline:
      - name: compoments.nlu.helpers.correction.TextCorrection # 文本纠错 Component
        model_dir: ...  # 模型地址
        threshold: float  # 阈值
    ```
3. 重新训练

#### 可参考实现
- 开源纠错[汇总](https://github.com/li-aolong/li-aolong.github.io/issues/12)

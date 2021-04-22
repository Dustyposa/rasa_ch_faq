## 追问的实现
#### 实现办法： 在 `core` 中更改 `RULE` 的预测结果。也就是把 特定的句式（目前使用的 `intent`)  根据上轮的 `intent`，来选择是否重复上轮的 `action`。
PS: 不能保证为最优思路，思路仅供参考。

#### 实现思路：
    依据强规则：
        - 上一轮是特定的 `intent`
        - 这一轮是特定的 `intent`
        - 重复上一轮的 `intent`
    那么需要修改 `intent` 的判定。我们先尝试在 `nlu` 中实现，未果。最后选择 `core` 的 `policy` 来实现。
    
#### 实现探究：
  1. 更改预测的 `intent` - 未果  
     原因：`nlu` 的 `pipeline` 处理时是无状态的，并不知道上一轮的  `intent`
  2. 实现 `policy`，首先尝试的 `MemoizationPolicy` 中实现。但是个人感觉这个应该是基于规则的，所以放弃掉了 `MemoizationPolicy` 选择了 `RulePolicy` （欢迎指正）


#### 备注
具体代码实现可以参考 [`ask_again_policy.py`](./ask_again_policy.py)，代码优化已完成。有 `BUG` 欢迎提交 `PR or Issue`。

欢迎各位大佬指教。

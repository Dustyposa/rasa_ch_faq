import xmnlp

xmnlp.set_model('./pre_models/xmnlp-models')
import time

t1 = time.time()
text = "不能适应体育专业选拔人材的要求"
replace_result = {}
for pair, result in xmnlp.checker(text, k=1).items():
    print(pair, result)
    if result[0][-1] > 1.0:
        replace_result[pair[0]] = result[0][0]
if replace_result:
    old_text = text
    tmp = list(text)
    for i, v in replace_result.items():
        tmp[i] = v
    text = "".join(tmp)
    print(old_text, text)
print(f"cost time: {time.time() - t1}")
t1 = time.time()
print(xmnlp.checker("吃饭了吗"))
print(f"cost time: {time.time() - t1}")

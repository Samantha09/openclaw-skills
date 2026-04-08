# Python 常见陷阱与反模式

## 1. 可变默认参数

```python
# 错误！列表在函数定义时创建，所有调用共享同一个列表
def append_to(element, target=[]):
    target.append(element)
    return target

print(append_to(1))  # [1]
print(append_to(2))  # [1, 2]  ← 意外！

# 正确
def append_to(element, target=None):
    if target is None:
        target = []
    target.append(element)
    return target
```

## 2. 闭包延迟绑定

```python
# 错误！所有 lambda 引用同一个 i
funcs = [lambda: i for i in range(5)]
print([f() for f in funcs])  # [4, 4, 4, 4, 4]

# 正确：使用默认参数立即绑定
funcs = [lambda i=i: i for i in range(5)]
print([f() for f in funcs])  # [0, 1, 2, 3, 4]
```

## 3. 隐式 False 陷阱

```python
# 错误：'0' 是真值！
value = '0'
if value:
    print("这会执行")  # '0' 是非空字符串，True

# 错误：None 和 0 都是 False，但语义不同
def f(x=None):
    if not x:  # x=0 时也会进入！
        x = 1

# 正确
def f(x=None):
    if x is None:  # 精确判断 None
        x = 1
```

## 4. 循环中拼接字符串

```python
# 错误：O(n²) 时间复杂度
result = ""
for item in items:
    result += str(item)

# 正确：O(n) 时间复杂度
result = "".join(str(item) for item in items)
```

## 5. 捕获所有异常

```python
# 错误：捕获一切，包括 KeyboardInterrupt、SystemExit
try:
    do_something()
except:
    pass

# 正确：明确指定异常类型
try:
    do_something()
except (ValueError, IOError) as e:
    handle_error(e)
```

## 6. == 比较 None

```python
# 错误：== 可能触发自定义 __eq__
if x == None:
    ...

# 正确：is 比较身份
if x is None:
    ...
```

## 7. 忘记 return

```python
# 错误：条件不满足时隐式返回 None
def get_value(key):
    if key in data:
        return data[key]
    # 忘记处理 key 不存在的情况！

# 正确
def get_value(key):
    if key in data:
        return data[key]
    raise KeyError(f"Key not found: {key}")
```

## 8. 文件资源泄漏

```python
# 错误：忘记关闭
f = open("file.txt")
data = f.read()
# f.close() 如果 read() 抛异常就不会执行

# 正确
with open("file.txt") as f:
    data = f.read()
```

## 9. 浮点数精度

```python
# 陷阱：浮点数不精确
0.1 + 0.2 == 0.3  # False

# 解决方案
from decimal import Decimal
Decimal('0.1') + Decimal('0.2') == Decimal('0.3')  # True

# 或者用误差比较
abs(0.1 + 0.2 - 0.3) < 1e-9  # True
```

## 10. 列表推导式中的多重 for

```python
# 难以理解
result = [(x, y) for x in range(10) for y in range(5) if x * y > 10]

# 应该用显式循环
result = []
for x in range(10):
    for y in range(5):
        if x * y > 10:
            result.append((x, y))
```

## 11. 默认 `__hash__` 丢失

```python
class Foo:
    def __init__(self, x):
        self.x = x
    def __eq__(self, other):
        return self.x == other.x

# __eq__ 定义后 __hash__ 变为 None，对象不可哈希
f = Foo(1)
d = {f: "value"}  # TypeError: unhashable type

# 需要同时定义 __hash__
def __hash__(self):
    return hash(self.x)
```

## 12. 全局变量在导入时求值

```python
# config.py
import time
START_TIME = time.time()  # 模块被导入时求值，不是使用时

# 每次导入都是同一个时间，不是调用时的时间
```

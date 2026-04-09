# 异步编程模式

## 何时用 sync，何时用 async

| 场景 | 推荐 | 原因 |
|------|------|------|
| HTTP 请求 | async | IO 等待，不阻塞事件循环 |
| 数据库查询（async 驱动） | async | IO 等待 |
| 文件 IO（大文件） | async + aiofiles | IO 等待 |
| CPU 密集型计算 | sync + 线程池 | 不阻塞事件循环 |
| 正则匹配、文本解析 | sync + 线程池 | CPU 密集 |
| 简单文件读写 | sync | 开销大于收益 |

## asyncio 核心模式

### 基础协程

```python
async def fetch(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        return await resp.json()
```

### 并发执行

```python
# 同时执行多个协程
results = await asyncio.gather(
    fetch(url1),
    fetch(url2),
    fetch(url3),
)

# 限制并发数
semaphore = asyncio.Semaphore(10)

async def limited_fetch(url: str):
    async with semaphore:
        return await fetch(url)
```

### 超时控制

```python
# Python 3.11+
async with asyncio.timeout(5.0):
    result = await slow_operation()

# 兼容写法
try:
    result = await asyncio.wait_for(slow_operation(), timeout=5.0)
except asyncio.TimeoutError:
    result = None
```

### 后台任务

```python
# 创建后台任务（保存引用防止被 GC）
tasks = []
for url in urls:
    task = asyncio.create_task(process(url))
    tasks.append(task)

results = await asyncio.gather(*tasks)
```

## 线程池调度

### 在协程中调用同步函数

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

pool = ThreadPoolExecutor(max_workers=4)

async def handler():
    loop = asyncio.get_running_loop()

    # 位置参数
    result = await loop.run_in_executor(pool, sync_func, arg1, arg2)

    # 关键字参数（必须用 partial）
    result = await loop.run_in_executor(pool, partial(sync_func, key=value))
```

### 线程池管理器

```python
class ExecutorManager:
    """管理多个命名线程池的单例."""
    _instance = None

    def __init__(self):
        self._executors: dict[str, ThreadPoolExecutor] = {}
        self.register("default", max_workers=4)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, name: str, max_workers: int = 4, prefix: str = "pool"):
        if name in self._executors:
            self._executors[name].shutdown(wait=False)
        self._executors[name] = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=f"{prefix}-{name}",
        )

    def get(self, name: str = "default") -> ThreadPoolExecutor:
        if name not in self._executors:
            self.register(name)
        return self._executors[name]

    def shutdown(self, wait: bool = True):
        for ex in self._executors.values():
            ex.shutdown(wait=wait)
        self._executors.clear()
```

## 常见陷阱

### 1. 阻塞事件循环

```python
# 错误！
async def bad():
    time.sleep(5)        # 阻塞
    requests.get(url)    # 阻塞

# 正确
async def good():
    await asyncio.sleep(5)
    async with aiohttp.ClientSession() as s:
        await s.get(url)
```

### 2. 忘记 await

```python
# 错误！返回 coroutine 对象
result = async_function()

# 正确
result = await async_function()
```

### 3. 嵌套 asyncio.run()

```python
# 错误！
async def outer():
    result = asyncio.run(inner())  # RuntimeError

# 正确
async def outer():
    result = await inner()
```

### 4. gather 未处理异常

```python
# 一个失败全部取消
results = await asyncio.gather(t1(), t2())

# 容错
results = await asyncio.gather(t1(), t2(), return_exceptions=True)
```

### 5. 可变默认参数

```python
# 错误！列表在模块加载时创建，所有调用共享
def f(items=[]):
    items.append(1)
    return items

# 正确
def f(items=None):
    if items is None:
        items = []
    return items
```

### 6. 闭包中的延迟绑定

```python
# 错误！所有 lambda 捕获的都是最后的 i
funcs = [lambda: i for i in range(5)]

# 正确
funcs = [lambda i=i: i for i in range(5)]
```

## aiohttp 客户端模式

### 反模式：每次请求创建新 session

```python
# 错误！每次调用都创建/销毁 session，开销大
async def fetch(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()
```

### 推荐：复用 session

```python
class ApiClient:
    """复用 aiohttp session 的 API 客户端."""

    def __init__(self, base_url: str, timeout: int = 120):
        self.base_url = base_url
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def fetch(self, path: str) -> dict:
        session = await self._get_session()
        async with session.post(f"{self.base_url}{path}", ...) as resp:
            return await resp.json()
```

### 批量请求的并发控制

```python
async def fetch_all(urls: list[str], max_concurrent: int = 10) -> list[str]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited_fetch(url: str) -> str:
        async with semaphore:
            return await fetch(url)

    return await asyncio.gather(
        *[limited_fetch(url) for url in urls],
        return_exceptions=True,
    )
```

## 测试中的 sys.path 处理

当测试文件在子目录（如 `tests/`）下，直接运行时需要将项目根目录加入路径：

```python
# tests/test_xxx.py
import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
```

这样既支持 `python tests/test_xxx.py` 直接运行，也支持 `pytest tests/test_xxx.py`。

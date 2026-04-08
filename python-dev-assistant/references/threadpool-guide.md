# 线程池管理指南

## ThreadPoolExecutor 基础

### 创建与使用

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

# 创建
with ThreadPoolExecutor(max_workers=4, thread_name_prefix="worker") as pool:
    # 提交任务
    future = pool.submit(function, arg1, arg2)

    # 获取结果
    result = future.result()
    result = future.result(timeout=10)  # 带超时

    # 批量提交
    futures = {pool.submit(process, item): item for item in items}
    for future in as_completed(futures):
        result = future.result()
```

### Workers 数量选择

| 任务类型 | 建议 | 公式 |
|----------|------|------|
| CPU 密集型 | CPU 核数 + 1 | `os.cpu_count() + 1` |
| IO 密集型 | CPU 核数 × 2~5 | `os.cpu_count() * 4` |
| 混合型 | 根据瓶颈调整 | 监控后调优 |

### 生命周期管理

```python
# 推荐方式：with 语句自动关闭
with ThreadPoolExecutor(max_workers=4) as pool:
    pool.submit(task)

# 手动管理
pool = ThreadPoolExecutor(max_workers=4)
try:
    pool.submit(task)
finally:
    pool.shutdown(wait=True)
```

## 在 asyncio 中使用线程池

### run_in_executor

```python
import asyncio
from functools import partial

async def main():
    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=4)

    # 位置参数
    result = await loop.run_in_executor(pool, sync_func, arg1)

    # 关键字参数
    result = await loop.run_in_executor(
        pool, partial(sync_func, key1=val1, key2=val2)
    )

    # None = 默认线程池
    result = await loop.run_in_executor(None, sync_func)
```

### 默认线程池 vs 自定义线程池

```python
# 默认线程池（无需创建，workers = min(32, os.cpu_count() + 4)）
await loop.run_in_executor(None, func)

# 自定义线程池（推荐用于控制并发）
pool = ThreadPoolExecutor(max_workers=4)
await loop.run_in_executor(pool, func)
```

## 命名线程池管理器

### 设计要点

1. **单例模式**: 全局唯一，避免重复创建
2. **命名注册**: 按用途区分线程池（default / heavy / light）
3. **自动创建**: 获取不存在的线程池时自动创建
4. **生命周期**: 统一 shutdown，防止资源泄漏

### 完整实现

```python
from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional


class ExecutorManager:
    """全局线程池管理器（单例）."""

    _instance: Optional[ExecutorManager] = None

    def __init__(self):
        self._executors: Dict[str, ThreadPoolExecutor] = {}
        self._max_concurrency: int = 8
        self._semaphore: Optional[asyncio.Semaphore] = None
        self.register("default", max_workers=4)

    @classmethod
    def get_instance(cls) -> ExecutorManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, name: str, max_workers: int = 4, prefix: str = "pool"):
        """注册或替换命名线程池."""
        if name in self._executors:
            self._executors[name].shutdown(wait=False)
        self._executors[name] = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=f"{prefix}-{name}",
        )

    def get(self, name: str = "default") -> ThreadPoolExecutor:
        """获取线程池，不存在则自动创建."""
        if name not in self._executors:
            self.register(name)
        return self._executors[name]

    def configure(self, max_concurrency: int = 8, prefix: str = "pool", **pools: int):
        """一次性配置并发数和多个线程池."""
        self._max_concurrency = max_concurrency
        self._semaphore = None
        for name, workers in pools.items():
            self.register(name, max_workers=workers, prefix=prefix)

    def get_semaphore(self) -> asyncio.Semaphore:
        """惰性创建并发信号量."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self._max_concurrency)
        return self._semaphore

    def shutdown(self, wait: bool = True):
        """关闭所有线程池."""
        for executor in self._executors.values():
            executor.shutdown(wait=wait)
        self._executors.clear()
        self._semaphore = None
```

### 使用示例

```python
# 配置
manager = ExecutorManager.get_instance()
manager.configure(
    max_concurrency=8,
    prefix="app",
    default=4,
    heavy=2,
    light=8,
)

# 获取线程池
pool = manager.get("heavy")

# 在协程中使用
async def handler():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(manager.get("heavy"), cpu_intensive_task)

# 关闭
manager.shutdown()
```

## 线程安全注意事项

### 不要做的

```python
# 不要在多个线程中修改共享可变状态
shared_list = []

def worker():
    shared_list.append(result)  # 不安全！
```

### 推荐做法

```python
from queue import Queue

# 使用 Queue 传递数据
result_queue = Queue()

def worker():
    result_queue.put(result)  # 线程安全

# 或者使用 Lock
import threading
lock = threading.Lock()
shared_list = []

def worker():
    with lock:
        shared_list.append(result)
```

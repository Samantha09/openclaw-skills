---
name: python-dev-assistant
description: |
  Python 通用开发助手，涵盖编码规范、并发编程（asyncio + 线程池）、
  装饰器模式、类型注解和测试实践。在以下场景使用：
  (1) 实现 Python 功能或修复 Bug，(2) 编写 asyncio 协程或线程池代码，
  (3) 使用装饰器/注册表模式，(4) 编写 pytest 测试，
  (5) 遵循 Google Python 风格规范。
---

# Python 通用开发助手

涵盖 Python 编码规范、并发编程、设计模式和测试实践的通用开发技能。

## 能力

1. **功能开发与 Bug 修复**
   - 遵循 Google Python 风格规范编写代码
   - 正确使用类型注解和文档字符串
   - 实现同步和异步功能

2. **并发编程**
   - asyncio 协程开发（事件循环、await、gather）
   - 线程池管理（ThreadPoolExecutor、run_in_executor）
   - 并发控制（Semaphore、Lock、Queue）

3. **设计模式**
   - 装饰器 + 注册表模式（函数元数据挂载 + 自动发现注册）
   - 单例模式、工厂模式
   - 上下文管理器

4. **测试与规范**
   - pytest + pytest-asyncio 编写测试
   - Google Python 风格规范
   - 规范的文档字符串和类型注解

## 工作流程

### 1. 理解任务

编码前：
- 阅读需求/Bug 描述
- 探索相关代码文件，理解现有模式和规范
- 确认功能应该是同步还是异步

### 2. 实现

- 遵循现有代码风格和项目约定
- 使用类型注解（至少覆盖公开 API）
- 编写 Google 风格的文档字符串
- 处理边界情况和错误

### 3. 测试

- 使用 pytest 编写单元测试
- 覆盖正常路径和异常路径
- 异步代码使用 `pytest-asyncio` 或 `asyncio.run()`
- 注意隔离：重置单例、mock 外部依赖

### 4. 提交

遵循 Conventional Commits 规范：
```
<类型>(<范围>): <描述>

类型：feat / fix / docs / style / refactor / test / chore
```

## 编码规范

遵循 Google Python 风格规范，核心要点：

### 命名

| 类型 | 公有 | 内部 |
|------|------|------|
| 模块/包 | `lower_with_under` | `_lower_with_under` |
| 类 | `CapWords` | `_CapWords` |
| 函数/方法 | `lower_with_under()` | `_lower_with_under()` |
| 常量 | `CAPS_WITH_UNDER` | `_CAPS_WITH_UNDER` |
| 变量/参数 | `lower_with_under` | `_lower_with_under` |

### 格式

- 行宽 80 字符（利用括号隐式续行，不用反斜杠）
- 4 空格缩进，不用 Tab
- 导入分组：标准库 → 第三方 → 本地，组间空行
- 序列尾部逗号：跨行时添加

### 文档字符串

```python
def fetch_rows(table_handle: Table, keys: Sequence[str]) -> Mapping[str, tuple]:
    """从表中获取数据行.

    参数:
        table_handle: 处于打开状态的 Table 实例.
        keys: 要获取的行键值序列.

    返回:
        键值到行数据的映射字典.

    抛出:
        IOError: 访问表时出现错误.
    """
```

### 类型注解

- 公开 API 必须注解
- 用 `X | None` 代替 `Optional[X]`（Python 3.10+）
- 用内置泛型 `list[int]` 代替 `List[int]`（Python 3.9+）
- 为复杂类型定义别名（大驼峰命名）

```python
def process(data: str, timeout: float | None = None) -> dict[str, Any]:
    ...
```

## 并发编程

### asyncio 协程

```python
import asyncio

async def fetch_data(url: str) -> dict:
    """异步获取数据."""
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        return await resp.json()

# 并发执行
results = await asyncio.gather(
    fetch_data(url1),
    fetch_data(url2),
)
```

**核心规则**：
- `async def` 定义的函数必须 `await` 调用
- 不要在 async 函数中使用阻塞调用（`time.sleep`、同步 IO）
- 用 `asyncio.sleep()` 替代 `time.sleep()`
- 使用 `asyncio.gather()` 并发执行多个协程

### 线程池

```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

# 创建线程池
pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="worker")

# 在协程中执行同步函数
loop = asyncio.get_running_loop()
result = await loop.run_in_executor(pool, sync_function, arg1, arg2)

# 关键字参数用 partial
from functools import partial
result = await loop.run_in_executor(pool, partial(sync_fn, key=value))
```

**核心规则**：
- CPU 密集型任务投递到线程池，避免阻塞事件循环
- `run_in_executor` 的第三个参数是位置参数，关键字参数用 `partial`
- 线程池需要显式关闭（`shutdown()`），推荐用 `with` 语句
- 线程池中避免修改共享可变状态

### 并发控制

```python
# Semaphore 控制并发数
semaphore = asyncio.Semaphore(10)

async def limited_task():
    async with semaphore:
        await do_work()

# Lock 保护共享状态
lock = asyncio.Lock()

async def safe_update():
    async with lock:
        shared_state["count"] += 1
```

### 线程池管理器模式

```python
class ExecutorManager:
    """单例线程池管理器."""
    _instance = None

    def __init__(self):
        self._executors: dict[str, ThreadPoolExecutor] = {}
        self.register("default", max_workers=4)

    @classmethod
    def get_instance(cls) -> ExecutorManager:
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
        for executor in self._executors.values():
            executor.shutdown(wait=wait)
        self._executors.clear()
```

## 装饰器 + 注册表模式

用于实现自动发现和注册的插件系统：

```python
from typing import Any, Callable, Optional, TypedDict, TypeVar, Union
from functools import wraps

class PluginMeta(TypedDict):
    name: str
    category: str
    handler: Optional[Callable]

T = TypeVar("T", bound=Union[Callable, Any])

def plugin(
    name: Optional[str] = None,
    category: str = "default",
) -> Callable[[T], T]:
    """插件注册装饰器，在函数上挂载元数据."""
    def decorator(fn: T) -> T:
        meta: PluginMeta = {
            "name": name or fn.__name__,
            "category": category,
            "handler": None,
        }
        setattr(fn, "plugin_meta", meta)
        return fn
    return decorator

class PluginRegistry:
    """自动扫描并注册带 @plugin 装饰器的函数."""

    def __init__(self):
        self._plugins: dict[str, Callable] = {}

    def load_from_path(self, path: str):
        """扫描目录，自动注册所有带 @plugin 的模块."""
        # 遍历目录，importlib 加载模块
        # 检查 hasattr(obj, "plugin_meta")
        # 注册到 self._plugins
        ...

    def get(self, name: str) -> Callable:
        return self._plugins[name]

    def list_plugins(self) -> list[str]:
        return list(self._plugins.keys())
```

## 测试实践

### pytest 基础

```python
import pytest

class TestMyFeature:
    @pytest.fixture(autouse=True)
    def setup(self):
        # 每个测试前执行
        yield
        # 每个测试后清理

    def test_basic(self):
        result = my_function("input")
        assert result == expected

    def test_error(self):
        with pytest.raises(ValueError):
            my_function("bad input")
```

### 异步测试

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function("input")
    assert result == expected

# 或者手动运行
def test_async_manual():
    result = asyncio.run(my_async_function("input"))
    assert result == expected
```

### 单例隔离

```python
@pytest.fixture(autouse=True)
def reset_singleton():
    MySingleton._instance = None
    yield
    MySingleton._instance = None
```

## 脚本

使用 `scripts/` 目录中的脚本进行常见操作：

- `analyze_changes.py` - 分析 git diff，识别受影响的 Python 模块
- `generate_commit.py` - 生成规范的 Conventional Commits 提交信息

## 参考资料

查看 `references/` 目录：
- `google-python-style-guide.md` - **Google Python 风格规范** — 命名、格式、注释、类型注解
- `google-python-language-rules.md` - **Google Python 语言规范** — 异常、导入、推导式、装饰器
- `async-patterns.md` - **异步编程模式** — asyncio 最佳实践和常见陷阱
- `threadpool-guide.md` - **线程池管理指南** — 配置、生命周期、调度原理

## 更新技能

```bash
cd ~/.openclaw/workspace/skills
rm -rf python-dev-assistant
curl -L https://github.com/Samantha09/openclaw-skills/archive/refs/heads/main.zip -o skills.zip
unzip skills.zip
mv openclaw-skills-main/python-dev-assistant .
rm -rf openclaw-skills-main skills.zip
```

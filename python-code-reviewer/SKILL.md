---
name: python-code-reviewer
description: |
  Python 代码审查助手，基于 Google Python 风格规范和并发编程最佳实践。
  在以下场景使用：(1) 审查 Pull Request / Merge Request，
  (2) 审查 asyncio 协程和线程池代码的正确性，
  (3) 检查类型注解、文档字符串、命名规范，
  (4) 识别 Python 常见反模式和安全隐患，
  (5) 生成结构化审查报告。
---

# Python 代码审查助手

基于 Google Python 风格规范和并发编程最佳实践的 Python 代码审查技能。

## 能力

1. **代码质量评估**
   - 检查代码是否符合 Google Python 风格规范
   - 评估可读性、可维护性和扩展性
   - 识别过度复杂、重复或死代码

2. **并发安全审查**
   - 检查 asyncio 协程使用是否正确（阻塞事件循环、忘记 await 等）
   - 审查线程池配置和生命周期管理
   - 识别竞态条件和共享状态问题

3. **类型与规范审查**
   - 验证类型注解的完整性和正确性
   - 检查文档字符串格式（Google 风格）
   - 审查命名规范、导入顺序、代码格式

4. **审查报告生成**
   - 按严重程度分类问题（BLOCKER / WARNING / SUGGESTION）
   - 输出结构化 Markdown 审查报告
   - 生成可直接用于 PR/MR 的评论

## 工作流程

### 1. 准备

审查前：
- 阅读需求/PR 描述，理解变更目标
- 获取 diff 范围
- 确认项目编码规范

### 2. 检查

逐文件逐变更检查，按以下维度：

- **规范**：命名、格式、导入、注释
- **正确性**：逻辑错误、边界条件、类型错误
- **安全性**：SQL 注入、XSS、敏感信息泄露、命令注入
- **性能**：不必要的对象创建、低效算法、循环内字符串拼接
- **可维护性**：函数长度、圈复杂度、硬编码、重复代码
- **并发**：asyncio 使用、线程池配置、共享状态、竞态条件
- **类型**：注解完整性、泛型参数、Optional/None 处理

### 3. 报告

汇总审查结果，输出包含以下字段的结构化报告：
- 文件路径和行号
- 问题级别：`BLOCKER` / `WARNING` / `SUGGESTION`
- 问题类别：规范 / 正确性 / 安全 / 性能 / 可维护性 / 并发
- 问题描述
- 修改建议
- 参考依据

### 4. 跟进

- 对修复后的代码进行再次审查
- 确认问题已解决且无新增问题

## 审查要点

### Python 规范（Google 风格）

**阻塞级 (BLOCKER)**：
- 函数默认参数为可变对象（`def f(x=[])`)
- 使用 `except:` 捕获所有异常
- 使用 `==` 比较 `None`（应该用 `is None`）
- 导入时使用相对路径

**警告级 (WARNING)**：
- 导入语句顺序不正确（标准库/第三方/本地混排）
- 函数超过 40 行未拆分
- 行宽超过 80 字符且可拆分
- 使用反斜杠续行（应该用括号）
- 文件缺少模块级文档字符串
- 公开 API 缺少类型注解

**建议级 (SUGGESTION)**：
- 类型注解不完整（缺少返回值类型）
- 文档字符串格式不符合 Google 风格
- 可以用推导式替代 map/filter + lambda
- 字符串格式化方式不一致（混用 f-string、format、%）

### 命名规范

**阻塞级 (BLOCKER)**：
- 使用首尾双下划线的名称（Python 保留名称）
- 单字符变量名用于非标准场景

**警告级 (WARNING)**：
- 类名不用 CapWords
- 函数/变量名不用 snake_case
- 常量不用 UPPER_SNAKE_CASE
- 文件名包含连字符

**建议级 (SUGGESTION)**：
- 变量名包含不必要的类型信息（如 `id_to_name_dict`）
- 缩写不常见、难以理解

### asyncio 与协程

**阻塞级 (BLOCKER)**：
- 在 async 函数中使用阻塞调用（`time.sleep`、`requests.get`、同步文件 IO）
- 忘记 `await`，导致返回 coroutine 对象而非结果
- 嵌套调用 `asyncio.run()`（在已有事件循环中）
- 在非 async 上下文中使用 `await`

**警告级 (WARNING)**：
- `asyncio.gather` 未处理单个任务的异常
- 后台任务未保存引用，可能被垃圾回收
- 使用 `asyncio.ensure_future` 而非 `asyncio.create_task`（3.7+）
- 长时间运行的协程没有超时控制
- aiohttp ClientSession 在循环中反复创建/销毁（应复用或传入）
- HTTP 请求缺少超时控制
- 响应解析未处理 content-type 差异（如期望 JSON 但返回 SSE）

**建议级 (SUGGESTION)**：
- 可用 `asyncio.timeout`（3.11+）替代手动超时管理
- 可添加协程取消支持（`CancelledError` 处理）

### 线程池与并发

**阻塞级 (BLOCKER)**：
- 在线程池中修改共享可变状态且无同步机制
- 线程池 shutdown 后仍尝试使用
- 线程池资源泄漏（未调用 shutdown）

**警告级 (WARNING)**：
- 线程池 workers 数量配置不合理
- `run_in_executor` 传参错误（关键字参数需要 `partial`）
- 使用无界队列导致潜在 OOM
- Semaphore 和线程池 workers 数量不匹配

**建议级 (SUGGESTION)**：
- 线程名缺少有意义的 prefix，不利于日志排查
- 可配置的参数硬编码在代码中

### 类型注解

**阻塞级 (BLOCKER)**：
- 使用隐式 Optional（`def f(x: str = None)` 应为 `str | None = None`）
- 泛型类型未填入参数（`dict` 而非 `dict[str, int]`）

**警告级 (WARNING)**：
- 使用旧的 `Optional[X]` 而非 `X | None`（3.10+）
- 使用 `typing.List` 而非 `list`（3.9+）
- `__init__` 注解了 `-> None`（不需要）

**建议级 (SUGGESTION)**：
- 复杂类型可以用别名简化，但未定义
- `# type: ignore` 注释缺少说明

### 安全审查

**阻塞级 (BLOCKER)**：
- 使用 `eval()` / `exec()` 处理用户输入
- SQL 拼接而非参数化查询
- 命令注入（`os.system` + 用户输入）
- 硬编码密码、API Key、Token

**警告级 (WARNING)**：
- 异常处理中暴露敏感信息到日志
- 文件操作使用用户提供的路径未做校验
- 使用 `pickle.loads` 处理不可信数据

**建议级 (SUGGESTION)**：
- 日志中使用 f-string 而非 `%` 格式化（影响日志聚合）
- 错误信息不够精确，难以定位问题

### 设计与可维护性

**阻塞级 (BLOCKER)**：
- 循环依赖（A 导入 B，B 导入 A）
- 全局可变状态被多处修改

**警告级 (WARNING)**：
- 一个函数承担多个职责
- 方法参数过多（> 5 个）且无数据类/字典封装
- 深层嵌套（> 3 层 if/for）
- 使用自定义元类、字节码操作等威力过大的功能

**建议级 (SUGGESTION)**：
- 方法行数超过 40 行，可拆分
- 存在重复代码块，可提取公共方法
- 可用 `dataclass` 替代手动 `__init__`

### 审查优先级

发现多个问题时，按以下优先级排序：
1. **阻塞级 (BLOCKER)**：可能导致运行时错误、数据丢失、安全漏洞
2. **警告级 (WARNING)**：明显违反规范、潜在 Bug、性能问题
3. **建议级 (SUGGESTION)**：可优化但非必须，涉及可读性和设计

## 脚本

使用 `scripts/` 目录中的脚本进行常见操作：

- `review_pr.py` - 基于 git diff 生成结构化代码审查报告
- `check_style.py` - 执行基础风格检查（行长度、导入顺序、命名等）

## 参考资料

查看 `references/` 目录：
- `code-review-checklist.md` - **代码审查检查清单** - 按维度划分的必查项
- `common-pitfalls.md` - **Python 常见陷阱与反模式** - 可变默认参数、闭包陷阱等
- `security-checklist.md` - **安全审查清单** - OWASP 常见漏洞在 Python 中的体现

同时也参考 `python-dev-assistant` 的规范：
- `references/google-python-style-guide.md` - Google Python 风格规范
- `references/google-python-language-rules.md` - Google Python 语言规范
- `references/async-patterns.md` - 异步编程最佳实践
- `references/threadpool-guide.md` - 线程池管理指南

## 更新技能

```bash
cd ~/.openclaw/workspace/skills
rm -rf python-code-reviewer
curl -L https://github.com/Samantha09/openclaw-skills/archive/refs/heads/main.zip -o skills.zip
unzip skills.zip
mv openclaw-skills-main/python-code-reviewer .
rm -rf openclaw-skills-main skills.zip
```

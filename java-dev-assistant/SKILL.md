---
name: java-dev-assistant
description: |
  Java 开发助手，专为 KimiCode 优化。处理 Java 功能开发、Bug 修复、
  规范提交、测试用例生成和文档记录。在以下场景使用：
  (1) 实现功能或修复 Bug，(2) 生成规范提交信息，(3) 基于代码变更创建测试用例，
  (4) 记录修改文档。
---

# Java 开发助手

为 KimiCode 优化的 Java 开发工作流技能。

## 能力

1. **功能开发与 Bug 修复**
   - 阅读和理解 Java 代码库
   - 按照项目规范实现新功能
   - 最小化影响地修复 Bug

2. **规范提交**
   - 遵循 Conventional Commits 规范生成提交信息
   - 包含类型、范围、描述和正文

3. **测试用例生成**
   - 分析代码变更
   - 生成覆盖修改逻辑的单元测试
   - 记录测试场景和边界情况

4. **文档记录**
   - 以结构化格式记录变更
   - 文档化影响范围和迁移说明

## 工作流程

### 1. 理解任务

编码前：
- 阅读需求/Bug 描述
- 探索相关代码文件
- 理解现有模式和规范

### 2. 实现

- 遵循现有代码风格
- 添加必要的导入
- 确保类型安全
- 处理边界情况

### 3. 提交生成

使用规范提交格式：
```
<类型>(<范围>): <描述>

<正文>

<页脚>
```

类型：`feat`（新功能）、`fix`（修复）、`docs`（文档）、`style`（格式）、`refactor`（重构）、`test`（测试）、`chore`（杂项）

### 4. 测试生成

对于每个变更：
- 识别受影响的方法/类
- 生成单元测试
- 覆盖正常情况、边界情况和错误场景

### 5. 文档记录

创建变更日志条目，包含：
- 变更摘要
- 修改的文件
- 影响范围
- 迁移说明（如有破坏性变更）

## 脚本

使用 `scripts/` 目录中的脚本进行常见操作：

- `analyze_changes.py` - 分析 git diff，识别受影响组件
- `generate_commit.py` - 生成规范提交信息
- `generate_tests.py` - 从代码变更生成测试用例

## 参考资料

查看 `references/` 目录：
- `alibaba-java-manual.md` - **阿里巴巴 Java 开发手册（嵩山版）** - 命名规范、编码规约、异常处理、并发、数据库等
- `commit-convention.md` - 提交信息格式详情
- `testing-guide.md` - 测试最佳实践
- `java-style-guide.md` - 项目代码规范

### 编码规范

开发 Java 代码时，请遵循 **阿里巴巴 Java 开发手册** 的规约：
- 命名风格：类名 UpperCamelCase，方法/变量 lowerCamelCase，常量 UPPER_SNAKE_CASE
- OOP 规约：POJO 类属性使用包装类型，重写 equals 必须重写 hashCode
- 集合处理：不要在 foreach 循环里进行 remove/add 操作
- 并发处理：线程池使用 ThreadPoolExecutor 创建，不要直接用 Executors
- 异常日志：使用 SLF4J，异常信息要包含案发现场和堆栈
- MySQL：表必备 id/create_time/update_time，禁用外键，不用 SELECT *

### 异步与并发编程

Java 异步编程最佳实践：
- **优先使用 CompletableFuture**：比 Future + Callable 更灵活，支持链式调用和组合
- **线程池必须通过 ThreadPoolExecutor 创建**：禁止使用 Executors 的便捷方法（固定、单例、缓存线程池），避免 OOM 和线程无限增长
- **合理配置线程池参数**：
  - corePoolSize：根据任务类型（IO 密集型 = CPU 核数*2，CPU 密集型 = CPU 核数+1）
  - maxPoolSize >= corePoolSize，且考虑系统承载能力
  - 使用有界队列（ArrayBlockingQueue/LinkedBlockingQueue 指定容量），避免无界队列导致 OOM
  - 设置拒绝策略（CallerRunsPolicy/DiscardPolicy/DiscardOldestPolicy）
  - 必须设置线程池名称，便于问题排查
- **异步任务异常处理**：使用 exceptionally()、handle() 处理异常，避免异常静默丢失
- **优雅关闭线程池**：先 shutdown()，再 awaitTermination()，必要时 shutdownNow()
- **避免在异步任务中共享可变状态**：使用 ThreadLocal 时要注意清理，防止内存泄漏
- **超时控制**：为异步任务设置超时（orTimeout/completeOnTimeout），防止无限等待

### 低耦合设计原则

构建低耦合系统的关键实践：
- **依赖接口而非实现**：使用接口/抽象类定义契约，通过依赖注入获取实例
- **分层架构**：Controller → Service → DAO/Repository，上层不直接访问下层实现细节
- **单一职责原则（SRP）**：每个类只负责一个功能领域，方法行数控制在 80 行以内
- **依赖倒置原则（DIP）**：高层模块不依赖低层模块，都依赖抽象
- **控制反转（IoC）**：通过 Spring 等容器管理依赖关系，避免 new 关键字硬编码
- **事件驱动解耦**：使用 Spring Event、MQ 等机制解耦模块间直接调用
- **配置与代码分离**：使用配置文件、环境变量、配置中心管理可变参数

### 可扩展性设计原则

构建可扩展系统的核心策略：
- **开闭原则（OCP）**：对扩展开放，对修改关闭。新增功能通过新增类实现，而非修改现有代码
- **策略模式**：将可变算法封装为独立策略类，通过上下文动态切换
- **模板方法模式**：定义算法骨架，将可变步骤延迟到子类实现
- **SPI 机制**：使用 Java SPI 或 Spring SPI 实现插件化扩展
- **工厂模式 + 注册表**：通过工厂统一管理对象创建，支持动态注册新类型
- **责任链模式**：将处理逻辑拆分为多个独立处理器，支持动态增减
- **数据结构与算法分离**：使用泛型和接口设计通用数据结构，业务逻辑通过回调传入
- **预留扩展点**：在关键流程中设计 Hook 接口或预留空方法，便于后续扩展
- **模块化设计**：按业务域划分模块，通过清晰 API 边界交互，支持独立演进

## 更新技能

### 从 GitHub 拉取最新版本

**方法 1：直接下载（推荐）**
```bash
# 进入 skills 目录
cd ~/.openclaw/workspace/skills

# 删除旧版本
rm -rf java-dev-assistant

# 下载最新版本
curl -L https://github.com/Samantha09/openclaw-skills/archive/refs/heads/main.zip -o skills.zip
unzip skills.zip
mv openclaw-skills-main/java-dev-assistant .
rm -rf openclaw-skills-main skills.zip
```

**方法 2：使用 Git 克隆**
```bash
# 进入 skills 目录
cd ~/.openclaw/workspace/skills

# 如果已克隆，直接拉取更新
if [ -d "openclaw-skills" ]; then
    cd openclaw-skills
    git pull origin main
else
    # 首次克隆
    git clone https://github.com/Samantha09/openclaw-skills.git
fi

# 同步到本地 skills 目录
cp -r openclaw-skills/java-dev-assistant .
```

**方法 3：手动更新**
1. 访问 https://github.com/Samantha09/openclaw-skills/tree/main/java-dev-assistant
2. 下载每个文件的最新内容
3. 替换 `~/.openclaw/workspace/skills/java-dev-assistant/` 中的对应文件

### 验证更新

更新后检查技能版本：
```bash
# 查看 SKILL.md 的修改日期
ls -la ~/.openclaw/workspace/skills/java-dev-assistant/SKILL.md

# 或者查看文件内容中的版本信息
head -5 ~/.openclaw/workspace/skills/java-dev-assistant/SKILL.md
```

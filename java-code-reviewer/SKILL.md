---
name: java-code-reviewer
description: |
  Java 代码审查助手，专为 KimiCode 优化。执行代码评审、发现潜在问题、提出改进建议。
  在以下场景使用：(1) 审查 Pull Request / Merge Request，(2) 评审本地代码变更，
  (3) 生成结构化审查报告，(4) 识别常见 Java 反模式和安全漏洞。
---

# Java 代码审查助手

为 KimiCode 优化的 Java 代码审查工作流技能。

## 能力

1. **代码质量评估**
   - 检查代码是否符合项目规范和阿里巴巴 Java 开发手册
   - 评估可读性、可维护性和扩展性
   - 识别过度复杂、重复或死代码

2. **问题发现**
   - 发现常见的 Java 反模式和潜在 Bug
   - 检查空安全、并发、异常处理和资源释放
   - 识别性能瓶颈和安全隐患

3. **审查报告生成**
   - 按严重程度分类问题（阻塞 / 警告 / 建议）
   - 输出结构化的 Markdown / JSON 审查报告
   - 生成可直接用于 PR/MR 的评论

4. **改进建议**
   - 针对每个问题给出具体、可执行的修改建议
   - 提供重构思路和最佳实践参考

## 工作流程

### 1. 准备

审查前：
- 阅读需求/设计文档，理解变更目标
- 获取 diff 范围（分支对比或本地暂存变更）
- 确认项目编码规范和审查清单

### 2. 检查

逐文件逐变更检查：
- **规范**：命名、格式、导入、注释
- **正确性**：逻辑错误、边界条件、并发问题
- **安全性**：SQL 注入、XSS、敏感信息泄露、越权
- **性能**：不必要的对象创建、低效算法、N+1 查询
- **可维护性**：方法长度、圈复杂度、硬编码、重复代码
- **异步/并发**：线程池配置、CompletableFuture 使用、竞态条件、死锁
- **可扩展性**：耦合度、是否符合开闭原则、扩展点设计

### 3. 报告

汇总审查结果，输出包含以下字段的结构化报告：
- 文件路径和行号
- 问题级别：`BLOCKER` / `WARNING` / `SUGGESTION`
- 问题类别：规范 / 正确性 / 安全 / 性能 / 可维护性
- 问题描述
- 修改建议
- 参考依据

### 4. 跟进

- 对修复后的代码进行再次审查
- 确认问题已解决且无新增问题
- 更新审查状态

## 脚本

使用 `scripts/` 目录中的脚本进行常见操作：

- `review_pr.py` - 基于 git diff 生成结构化代码审查报告
- `check_style.py` - 执行基础风格检查（行长度、魔法值、Tab 等）

## 参考资料

查看 `references/` 目录：
- `code-review-checklist.md` - **代码审查检查清单** - 按维度划分的必查项
- `common-pitfalls.md` - **Java 常见陷阱与反模式** - 空指针、并发、集合、异常等
- `security-checklist.md` - **安全审查清单** - OWASP 常见漏洞在 Java 中的体现

同时也参考 `java-dev-assistant` 的规范：
- `alibaba-java-manual.md` - 阿里巴巴 Java 开发手册
- `java-style-guide.md` - 项目代码风格指南
- `testing-guide.md` - 测试规范（检查测试覆盖率和质量）

### 异步与线程池审查要点

**阻塞级 (BLOCKER)**：
- 使用 Executors 创建线程池（Executors.newFixedThreadPool 等）
- 使用无界队列（LinkedBlockingQueue 不指定容量）
- 未设置线程池名称，无法排查问题
- CompletableFuture 异常未处理导致异常静默丢失
- 异步任务中修改共享可变状态且无同步机制

**警告级 (WARNING)**：
- 线程池参数配置不合理（corePoolSize = maxPoolSize 且使用无界队列时无法扩容）
- 未设置拒绝策略或使用默认 AbortPolicy 但未处理 RejectedExecutionException
- 未对异步任务设置超时，可能导致无限等待
- ThreadLocal 在线程池中使用后未清理
- 线程池未提供优雅关闭机制

**建议级 (SUGGESTION)**：
- 可使用并行流/CompletableFuture 简化同步代码的地方仍使用手动线程管理
- 异步任务未记录执行日志，难以追踪问题

### 低耦合审查要点

**阻塞级 (BLOCKER)**：
- 上层直接依赖下层具体实现类，而非接口
- 循环依赖（A 依赖 B，B 又依赖 A）

**警告级 (WARNING)**：
- 一个类承担多个职责（方法数 > 30 或功能域混杂）
- 方法参数过多（> 5 个）且无 Builder/参数对象
- 直接使用 new 创建复杂依赖对象，而非通过工厂/容器
- 硬编码配置信息（数据库连接、外部服务地址等）

**建议级 (SUGGESTION)**：
- 方法行数超过 80 行，可拆分为多个小方法
- 存在重复代码块，可提取为公共方法

### 可扩展性审查要点

**阻塞级 (BLOCKER)**：
- 新增功能需要修改大量现有类（违反开闭原则）
- 使用 if-else/switch 枚举所有类型且频繁扩展，未使用策略模式

**警告级 (WARNING)**：
- 核心流程缺乏扩展点/Hook 机制，后续扩展困难
- 数据结构设计与业务逻辑耦合过紧，无法复用
- 缺少 SPI 或插件化机制，新功能只能侵入式修改

**建议级 (SUGGESTION)**：
- 可使用泛型 + 回调实现通用逻辑的地方写死类型
- 关键算法未预留参数化配置，只能硬编码

### 审查优先级

发现多个问题时，按以下优先级排序：
1. **阻塞级 (BLOCKER)**：可能导致生产故障、数据丢失、安全漏洞
2. **警告级 (WARNING)**：明显违反规范、潜在 Bug、性能问题
3. **建议级 (SUGGESTION)**：可优化但非必须，涉及可读性和设计

## 更新技能

更新方式与 `java-dev-assistant` 一致：

```bash
cd ~/.openclaw/workspace/skills
rm -rf java-code-reviewer
curl -L https://github.com/Samantha09/openclaw-skills/archive/refs/heads/main.zip -o skills.zip
unzip skills.zip
mv openclaw-skills-main/java-code-reviewer .
rm -rf openclaw-skills-main skills.zip
```

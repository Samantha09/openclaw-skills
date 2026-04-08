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
   - 检查代码是否符合阿里巴巴 Java 开发手册和项目规范
   - 评估可读性、可维护性和扩展性
   - 识别过度复杂、重复或死代码

2. **Spring Boot 审查**
   - 检查 Controller/Service/Repository 分层是否正确
   - 审查依赖注入方式（构造器注入 vs 字段注入）
   - 检查事务管理（@Transactional 使用是否正确）
   - 配置管理是否规范

3. **并发安全审查**
   - 检查线程池创建方式（禁用 Executors，必须用 ThreadPoolExecutor）
   - 审查 CompletableFuture 异常处理
   - 识别竞态条件和锁顺序问题
   - Java 21+ Virtual Thread 使用审查

4. **数据库与 ORM 审查**
   - 检查 SQL 注入风险、N+1 查询
   - 审查 MyBatis/JPA 映射和查询效率
   - 索引使用和分页查询是否合理

5. **日志审查**
   - 是否使用 SLF4J 而非 Log4j/Logback 直接调用
   - 日志级别是否恰当
   - 异常日志是否包含案发现场和堆栈
   - 敏感信息是否脱敏

6. **审查报告生成**
   - 按严重程度分类问题（BLOCKER / WARNING / SUGGESTION）
   - 输出结构化 Markdown 审查报告
   - 生成可直接用于 PR/MR 的评论

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
- **Spring Boot**：分层是否正确、注入方式、事务管理、配置管理
- **数据库/ORM**：SQL 拼接、N+1 查询、缺少索引、select *
- **日志**：SLF4J 使用、日志级别、异常堆栈、敏感信息脱敏

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
- `spring-boot-guide.md` - Spring Boot 开发指南
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

### Spring Boot 审查要点

**阻塞级 (BLOCKER)**：
- Controller 中包含业务逻辑（应下沉到 Service）
- @Transactional 加在 private 方法上（不生效）
- 使用 @Autowired 字段注入而非构造器注入
- 事务方法内部同类调用（self-invocation，事务不生效）

**警告级 (WARNING)**：
- Service 直接返回 Entity 而非 VO/DTO（暴露内部结构）
- @Transactional 未指定 rollbackFor（默认只回滚 RuntimeException）
- 使用 @Value 逐个读取配置而非 @ConfigurationProperties
- RestTemplate 未配置超时和连接池

**建议级 (SUGGESTION)**：
- 可用 @RequiredArgsConstructor 替代手写构造器
- 可用 Spring Cache 替代手动缓存管理

### 数据库与 ORM 审查要点

**阻塞级 (BLOCKER)**：
- SQL 拼接（`"SELECT * FROM " + table + " WHERE id = " + id`）
- MyBatis 使用 `${}` 而非 `#{}`（SQL 注入）
- 大表全表扫描（缺少 WHERE 条件或索引）

**警告级 (WARNING)**：
- N+1 查询（循环内单条查询）
- 使用 `SELECT *` 而非指定字段
- 分页查询未做 count=0 判断
- ArrayList 批量插入（应用批量操作或 MyBatis batch）

**建议级 (SUGGESTION)**：
- 可用延迟关联优化深分页
- IN 子句元素过多（> 1000）应分批处理

### 日志审查要点

**阻塞级 (BLOCKER)**：
- 日志中打印密码、Token、身份证号等敏感信息
- 直接使用 System.out.println 输出日志

**警告级 (WARNING)**：
- 使用 Log4j/Logback API 而非 SLF4J
- 异常日志缺少堆栈信息（`log.error("错误: " + e.getMessage())` 应为 `log.error("错误: {}", param, e)`）
- debug/trace 日志未用条件判断或占位符
- 使用 `e.printStackTrace()` 而非日志框架

**建议级 (SUGGESTION)**：
- 日志级别不恰当（正常业务用 error）
- 日志缺少上下文信息（如 userId、orderId）

### Virtual Thread (Java 21+) 审查要点

**阻塞级 (BLOCKER)**：
- 在 Virtual Thread 中使用 synchronized 同步块（会 pin 住载体线程，应改用 ReentrantLock）
- Virtual Thread 中使用 ThreadLocal 大量存储数据（不回收导致内存泄漏）

**警告级 (WARNING)**：
- 在 Virtual Thread 中执行 CPU 密集型任务（应使用平台线程池）
- 混用 Virtual Thread 和传统线程池的同步原语

**建议级 (SUGGESTION)**：
- 使用 `Executors.newVirtualThreadPerTaskExecutor()` 创建虚拟线程
- 框架迁移时可先用 `-Djdk.virtualThreadScheduler.parallelism` 调优

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

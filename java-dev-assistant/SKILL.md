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

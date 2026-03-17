---
name: java-dev-assistant
description: |
  Java development assistant for KimiCode. Handles Java feature development, bug fixes, 
  standardized commits, test case generation, and documentation. Use when working with 
  Java projects to: (1) Implement features or fix bugs, (2) Generate conventional commits, 
  (3) Create test cases based on code changes, (4) Document modifications.
---

# Java Development Assistant

A comprehensive skill for Java development workflows optimized for KimiCode.

## Capabilities

1. **Feature Development & Bug Fixing**
   - Read and understand Java codebase
   - Implement new features following project conventions
   - Fix bugs with minimal impact

2. **Standardized Commits**
   - Generate commit messages following Conventional Commits specification
   - Include type, scope, description, and body

3. **Test Case Generation**
   - Analyze code changes
   - Generate unit tests covering modified logic
   - Document test scenarios and edge cases

4. **Documentation**
   - Record changes in structured format
   - Document impact scope and migration notes

## Workflow

### 1. Understanding the Task

Before coding:
- Read the requirement/bug description
- Explore relevant code files
- Understand existing patterns and conventions

### 2. Implementation

- Follow existing code style
- Add necessary imports
- Ensure type safety
- Handle edge cases

### 3. Commit Generation

Use conventional commit format:
```
<type>(<scope>): <description>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### 4. Test Generation

For each change:
- Identify affected methods/classes
- Generate unit tests
- Cover normal cases, edge cases, and error scenarios

### 5. Documentation

Create change log entry with:
- Summary of changes
- Modified files
- Impact scope
- Migration notes (if breaking)

## Scripts

Use scripts in `scripts/` directory for common operations:

- `analyze_changes.py` - Analyze git diff and identify affected components
- `generate_commit.py` - Generate conventional commit message
- `generate_tests.py` - Generate test cases from code changes

## References

See `references/` for:
- `alibaba-java-manual.md` - **阿里巴巴 Java 开发手册（嵩山版）** - 命名规范、编码规约、异常处理、并发、数据库等
- `commit-convention.md` - Commit message format details
- `testing-guide.md` - Testing best practices
- `java-style-guide.md` - Project coding conventions

### Coding Standards

开发 Java 代码时，请遵循 **阿里巴巴 Java 开发手册** 的规约：
- 命名风格：类名 UpperCamelCase，方法/变量 lowerCamelCase，常量 UPPER_SNAKE_CASE
- OOP 规约：POJO 类属性使用包装类型，重写 equals 必须重写 hashCode
- 集合处理：不要在 foreach 循环里进行 remove/add 操作
- 并发处理：线程池使用 ThreadPoolExecutor 创建，不要直接用 Executors
- 异常日志：使用 SLF4J，异常信息要包含案发现场和堆栈
- MySQL：表必备 id/create_time/update_time，禁用外键，不用 SELECT *

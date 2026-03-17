# Java 代码风格指南

## 通用原则

1. 遵循现有项目规范
2. 使用有意义的命名
3. 保持方法小而专注
4. 优先使用不可变性
5. 文档化公共 API

## 命名规范

| 元素 | 规范 | 示例 |
|------|------|------|
| 类名 | PascalCase，名词 | `UserService`, `OrderProcessor` |
| 方法名 | camelCase，动词 | `getUserById()`, `processOrder()` |
| 变量名 | camelCase | `userCount`, `orderList` |
| 常量名 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 包名 | 全小写 | `com.company.service` |

## 代码格式

### 缩进
- 使用 4 个空格（不用 tab）
- 续行缩进：8 个空格

### 大括号
- 左大括号在同一行
- 右大括号在新行

```java
if (condition) {
    doSomething();
} else {
    doSomethingElse();
}
```

### 行长度
- 最大 120 字符
- 在逻辑点处断行长行

## 导入

- 不使用通配符导入
- 分组导入：java、javax、org、com
- 静态导入放最后

```java
import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Service;

import com.company.project.model.User;
```

## 文档

### Javadoc

```java
/**
 * 方法的简要描述。
 *
 * @param paramName 参数描述
 * @return 返回值描述
 * @throws ExceptionType 何时抛出此异常
 */
```

### TODO 注释

```java
// TODO: 需要做什么的简要描述
// TODO(作者): 带指派人的描述
```

## 最佳实践

1. **空安全**：使用 Optional 代替 null
2. **集合**：声明时使用接口（List、Set、Map）
3. **流**：优先使用 Stream API 处理集合操作
4. **异常**：可恢复的错误使用受检异常
5. **日志**：使用 SLF4J，选择合适的日志级别

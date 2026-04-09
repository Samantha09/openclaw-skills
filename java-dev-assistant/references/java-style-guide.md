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
| 类名 | UpperCamelCase，名词 | `UserService`, `OrderProcessor` |
| 抽象类 | Abstract 或 Base 开头 | `AbstractBaseDAO`, `BaseController` |
| 异常类 | Exception 结尾 | `UserNotFoundException` |
| 测试类 | 以被测试类名开始，Test 结尾 | `UserServiceTest` |
| 方法名 | lowerCamelCase，动词 | `getUserById()`, `processOrder()` |
| 变量名 | lowerCamelCase | `userCount`, `orderList` |
| 常量名 | UPPER_SNAKE_CASE，语义完整 | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| 包名 | 全小写，单数形式 | `com.company.service` |
| 枚举类 | Enum 后缀，成员全大写 | `DealStatusEnum` / `SUCCESS / UNKNOWN_REASON` |
| 数组 | 中括号跟类型 | `String[] args`（禁止 `String args[]`） |
| POJO 布尔 | 不加 is 前缀 | `deleted`（不是 `isDeleted`） |
| 设计模式 | 类名体现模式 | `OrderFactory`, `LoginProxy`, `ResourceObserver` |
| 接口方法 | 无修饰符 | `void f();`（不加 `public abstract`） |
| Service/DAO 方法 | get/list/count/save/remove/update | `getUser()`, `listOrders()`, `countByStatus()` |
| DO | xxxDO，xxx 为表名 | `UserDO` |
| DTO | xxxDTO，xxx 为业务领域 | `UserDTO` |
| VO | xxxVO，xxx 为网页名 | `UserVO` |

## 代码格式

### 缩进
- 使用 4 个空格（不用 tab）
- 续行缩进：4 个空格（第二行相对第一行缩进 4 个空格，第三行起不再继续缩进）

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

1. **空安全**：使用 Optional 代替 null，防止 NPE 是程序员的基本修养
2. **集合**：声明时使用接口（List、Set、Map），初始化时指定大小
3. **流**：优先使用 Stream API 处理集合操作，遍历 Map 使用 entrySet
4. **异常**：可恢复的错误使用受检异常，使用有业务含义的自定义异常
5. **日志**：使用 SLF4J，选择合适的日志级别，异常日志包含案发现场和堆栈
6. **覆写**：所有覆写方法必须加 @Override
7. **比较**：包装类对象比较使用 equals，不用 ==（Integer -128~127 有缓存）
8. **常量**：禁止魔法值，常量按功能分类维护
9. **构造器**：构造方法中禁止业务逻辑，POJO 类必须写 toString
10. **访问控制**：从严控制，类成员变量尽量 private，方法范围最小化
11. **正则**：利用预编译功能，不要在方法体内定义 Pattern
12. **时间**：获取毫秒数用 System.currentTimeMillis()，JDK8 用 Instant
13. **final**：善用 final 修饰不可变类、域变量、方法、局部变量
14. **线程池**：必须通过 ThreadPoolExecutor 创建，禁止 Executors
15. **switch**：必须有 default，case 必须有 break/return
16. **if-else**：超过 3 层使用卫语句、策略模式或状态模式

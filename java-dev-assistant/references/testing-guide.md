# 测试指南

## 测试框架

使用 JUnit 5 (Jupiter) 进行单元测试。

## 测试结构

```java
@Test
@DisplayName("描述性测试名称")
void 方法名_场景_预期结果() {
    // 准备 - 设置测试数据和 Mock
    
    // 执行 - 执行被测试的方法
    
    // 验证 - 验证结果
}
```

## 测试命名规范

格式：`方法名_场景_预期结果`

示例：
- `calculatePrice_validInput_returnsCorrectTotal`
- `processOrder_nullOrder_throwsIllegalArgumentException`
- `getUser_nonExistentUser_returnsEmptyOptional`

## 测试类别

### 1. 正向测试
- 有效输入
- 正常操作流程
- 预期成功结果

### 2. 边界情况
- Null 输入
- 空集合
- 边界值（Integer.MAX_VALUE、空字符串）

### 3. 异常测试
- 无效输入
- 错误条件
- 预期异常

### 4. 集成点
- 外部服务调用
- 数据库交互
- 文件 I/O 操作

## Mock

使用 Mockito 进行依赖 Mock：

```java
@Mock
private UserRepository userRepository;

@BeforeEach
void setUp() {
    MockitoAnnotations.openMocks(this);
}

@Test
void findUser_existingUser_returnsUser() {
    when(userRepository.findById(1L)).thenReturn(Optional.of(user));
    
    User result = service.findUser(1L);
    
    assertEquals(user, result);
    verify(userRepository).findById(1L);
}
```

## 断言

使用 AssertJ 进行流式断言：

```java
import static org.assertj.core.api.Assertions.*;

assertThat(result)
    .isNotNull()
    .hasSize(3)
    .containsExactlyInAnyOrder("a", "b", "c");

assertThatThrownBy(() -> service.process(null))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessageContaining("input cannot be null");
```

## 覆盖率目标

- 行覆盖率：>= 80%
- 分支覆盖率：>= 70%
- 关键路径：100%

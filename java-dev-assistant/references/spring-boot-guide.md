# Spring Boot 开发指南

## 分层架构

```
Controller (Web 层)
    ↓ 参数校验、转发
Service (业务逻辑层)
    ↓ 事务管理
Manager (通用业务层, 可选)
    ↓ 多 DAO 组合、第三方封装
Repository/DAO (数据访问层)
    ↓
Database
```

## 依赖注入

### 构造器注入（推荐）

```java
@Service
@RequiredArgsConstructor  // Lombok 生成构造器
public class UserServiceImpl implements UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;
}
```

### 不推荐的方式

```java
// 不推荐：字段注入
@Service
public class UserServiceImpl {
    @Autowired  // 难以测试、隐藏依赖关系
    private UserRepository userRepository;
}
```

## 配置管理

### @ConfigurationProperties（推荐）

```java
@ConfigurationProperties(prefix = "app.mail")
@Validated
public record MailProperties(
    @NotBlank String host,
    @Min(1) @Max(65535) int port,
    @NotBlank String from,
    boolean enabled
) {}
```

```yaml
# application.yml
app:
  mail:
    host: smtp.example.com
    port: 587
    from: noreply@example.com
    enabled: true
```

### @Value（简单场景可用）

```java
@Value("${app.mail.timeout:5000}")
private long timeout;
```

## 事务管理

```java
@Service
@RequiredArgsConstructor
public class OrderServiceImpl implements OrderService {
    private final OrderRepository orderRepository;
    private final InventoryService inventoryService;

    @Transactional(rollbackFor = Exception.class)  // 所有异常都回滚
    @Override
    public OrderVO createOrder(OrderCreateRequest request) {
        // 业务逻辑
        Order order = orderRepository.save(buildOrder(request));
        inventoryService.deduct(request.getSkuId(), request.getQuantity());
        return OrderConverter.toVO(order);
    }
}
```

**注意事项**：
- `@Transactional` 加在 public 方法上（private 不生效）
- 同类内部调用事务不生效（self-invocation，需要用 `AopContext.currentProxy()` 或拆分类）
- 必须指定 `rollbackFor = Exception.class`（默认只回滚 RuntimeException）
- 只读操作用 `@Transactional(readOnly = true)`

## Controller 规范

```java
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Tag(name = "用户管理")  // Swagger
public class UserController {
    private final UserService userService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "创建用户")
    public ResponseEntity<UserVO> create(
            @Valid @RequestBody UserCreateRequest request) {
        return ResponseEntity.ok(userService.create(request));
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserVO> getById(@PathVariable Long id) {
        return ResponseEntity.ok(userService.getById(id));
    }

    @GetMapping
    public ResponseEntity<PageResult<UserVO>> list(
            @Valid UserQueryRequest request) {
        return ResponseEntity.ok(userService.list(request));
    }
}
```

**注意事项**：
- Controller 不写业务逻辑，只做参数校验和转发
- 返回 VO/DTO，不返回 Entity
- 使用 `@Valid` 触发参数校验
- URL 使用 kebab-case：`/user-orders`

## 异常处理

### 全局异常处理器

```java
@ControllerAdvice
@RequiredArgsConstructor
public class GlobalExceptionHandler {
    private final Logger log = LoggerFactory.getLogger(getClass());

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusiness(BusinessException e) {
        log.warn("业务异常: code={}, msg={}", e.getErrorCode(), e.getMessage());
        return ResponseEntity.badRequest()
            .body(new ErrorResponse(e.getErrorCode(), e.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
            .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
            .collect(Collectors.joining("; "));
        return ResponseEntity.badRequest()
            .body(new ErrorResponse("INVALID_PARAM", message));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleUnexpected(Exception e) {
        log.error("未预期异常", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("INTERNAL_ERROR", "服务异常，请稍后重试"));
    }
}
```

### 自定义业务异常

```java
@Getter
public class BusinessException extends RuntimeException {
    private final String errorCode;

    public BusinessException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public BusinessException(String errorCode, String message, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
    }
}
```

## 测试

### Spring Boot Test

```java
@SpringBootTest
@ActiveProfiles("test")
@RequiredArgsConstructor
class UserServiceIntegrationTest {
    private final UserService userService;

    @Test
    void createUser_validRequest_returnsUser() {
        var request = new UserCreateRequest("test@example.com", "Test User");
        var result = userService.create(request);
        assertThat(result.getEmail()).isEqualTo("test@example.com");
    }
}
```

### Mock 测试

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock private UserRepository userRepository;
    @InjectMocks private UserServiceImpl userService;

    @Test
    void getById_existingUser_returnsUser() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(buildUser()));

        UserVO result = userService.getById(1L);

        assertThat(result.getName()).isEqualTo("Test User");
        verify(userRepository).findById(1L);
    }
}
```

# 阿里巴巴 Java 开发手册（嵩山版）

基于阿里巴巴 Java 开发手册（嵩山版）的规约集合，作为 Java 开发的规范参考。

## 一、编程规约

### 1.1 命名风格

| 类型 | 规约 | 示例 |
|------|------|------|
| 类名 | UpperCamelCase，名词 | `UserService`, `OrderProcessor` |
| 方法名 | lowerCamelCase，动词 | `getUserById()`, `processOrder()` |
| 变量名 | lowerCamelCase | `userCount`, `orderList` |
| 常量名 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| 包名 | 全小写，点分隔 | `com.company.module.service` |

**强制规定**:
- 代码中的命名严禁使用拼音与英文混合的方式
- 类名使用 UpperCamelCase，DO / BO / DTO / VO / AO / PO / UID 等除外
- 方法名、参数名、成员变量、局部变量都统一使用 lowerCamelCase
- 常量命名全部大写，单词间用下划线隔开
- 抽象类命名使用 Abstract 或 Base 开头
- 异常类命名使用 Exception 结尾
- 测试类命名以它要测试的类的名称开始，以 Test 结尾

**示例**:

```java
// 正确
public class UserServiceImpl implements UserService { }
public abstract class AbstractBaseDAO { }
public class UserNotFoundException extends RuntimeException { }
private static final int MAX_RETRY_COUNT = 3;

// 错误
public class userService { }                    // 类名不是 UpperCamelCase
public class AbstractbaseDao { }                // Base 后首字母未大写
private static final int maxRetryCount = 3;     // 常量不是 UPPER_SNAKE_CASE
int a, b, c;                                    // 禁止单字符命名（临时变量除外）
```

### 1.2 常量定义

- 不允许使用魔法值（即未经预先定义的常量）直接出现在代码中
- long 或 Long 初始赋值时，使用大写的 L，不能是小写的 l
- 不要使用一个常量类维护所有常量，应该按常量功能进行归类

### 1.3 代码格式

- 大括号的使用约定：左大括号前不换行，左大括号后换行，右大括号前换行
- 缩进：4 个空格，禁止使用 tab 字符
- 单行字符数限制不超过 120 个
- 方法体内的执行语句组、变量的定义语句组、不同的业务逻辑之间插入一个空行

### 1.4 OOP 规约

- 避免通过一个类的对象引用访问此类的静态变量或静态方法
- 所有的覆写方法，必须加 @Override 注解
- 相同参数类型，相同业务含义，才可以使用 Java 的可变参数
- 外部正在调用或者二方库依赖的接口，不允许修改方法签名
- 不能使用过时的类或方法
- Object 的 equals 方法容易抛空指针异常，应使用常量或确定有值的对象来调用 equals
- 所有的相同类型的包装类对象之间值的比较，全部使用 equals 方法比较
- 关于基本数据类型与包装数据类型的使用标准如下：
  - 【强制】所有的 POJO 类属性必须使用包装数据类型
  - 【强制】RPC 方法的返回值和参数必须使用包装数据类型
  - 【推荐】所有的局部变量使用基本数据类型

### 1.5 集合处理

- 关于 hashCode 和 equals 的处理，遵循如下规则：
  - 只要重写 equals，就必须重写 hashCode
  - Set 存储的是不重复的对象，依据 hashCode 和 equals 进行判断
  - 如果自定义对象作为 Map 的键，那么必须重写 hashCode 和 equals
- ArrayList 的 subList 结果不可强转成 ArrayList
- 使用集合转数组的方法，必须使用集合的 toArray(T[] array)
- 使用工具类 Arrays.asList() 把数组转换成集合时，不能使用其修改集合相关的方法
- 不要在 foreach 循环里进行元素的 remove/add 操作
- 在 JDK 7 版本及以上，Comparator 要满足自反性、传递性、对称性

### 1.6 并发处理

- 获取单例对象需要保证线程安全，其中的方法也要保证线程安全
- 创建线程或线程池时请指定有意义的线程名称
- 线程资源必须通过线程池提供，不允许在应用中自行显式创建线程
- 线程池不允许使用 Executors 去创建，而是通过 ThreadPoolExecutor 的方式
- SimpleDateFormat 是线程不安全的类，一般不要定义为 static 变量
- 高并发时，同步调用应该去考量锁的性能损耗
- 对多个资源、数据库表、对象同时加锁时，需要保持一致的加锁顺序
- 并发修改同一记录时，避免更新丢失，需要加锁
- 如果线程访问的是无锁的，那么使用乐观锁；如果访问的是有锁的，那么使用悲观锁

**示例**:

```java
// 错误：使用 Executors 创建线程池（无界队列可能导致 OOM）
ExecutorService pool = Executors.newFixedThreadPool(10);

// 正确：通过 ThreadPoolExecutor 显式指定参数
ThreadFactory namedFactory = r -> {
    Thread t = new Thread(r);
    t.setName("order-process-" + t.getId());
    return t;
};
ExecutorService pool = new ThreadPoolExecutor(
    4, 8, 60L, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(100),        // 有界队列
    namedFactory,
    new ThreadPoolExecutor.CallerRunsPolicy()
);

// 错误：SimpleDateFormat 线程不安全
private static final SimpleDateFormat SDF = new SimpleDateFormat("yyyy-MM-dd");

// 正确：使用 DateTimeFormatter（线程安全）
private static final DateTimeFormatter DTF = DateTimeFormatter.ofPattern("yyyy-MM-dd");

// 错误：双检锁未用 volatile
private static Singleton instance;
public static Singleton getInstance() {
    if (instance == null) {
        synchronized (Singleton.class) {
            if (instance == null) {
                instance = new Singleton();  // 可能读到半初始化对象
            }
        }
    }
    return instance;
}

// 正确：加 volatile 防止指令重排序
private static volatile Singleton instance;
```

### 1.7 控制语句

- 在一个 switch 块内，每个 case 要么通过 break/return 等来终止，要么注释说明程序将继续执行到哪一个 case 为止
- 当 switch 括号内的变量类型为 String 并且此变量为外部参数时，必须先进行 null 判断
- 在 if/else/for/while/do 语句中必须使用大括号，即使只有一行代码
- 表达异常的分支时，少用 if-else 方式，这种方式可以改写成卫语句
- 除常用方法（如 getXxx/isXxx）等外，不要在条件判断中执行复杂的语句

### 1.8 注释规约

- 类、类属性、类方法的注释必须使用 Javadoc 规范
- 所有的抽象方法（包括接口中的方法）必须要用 Javadoc 注释
- 所有的类都必须添加创建者和创建日期
- 方法内部单行注释，在被注释语句上方另起一行，使用 // 注释
- 方法内部多行注释使用 /* */ 注释，注意与代码对齐
- 所有的枚举类型字段必须要有注释，说明每个数据项的用途

---

## 二、异常日志

### 2.1 异常处理

- Java 类库中定义的可以通过预检查方式规避的 RuntimeException 异常不应该通过 catch 的方式来处理
- 异常不要用来做流程控制，条件控制
- catch 时请分清稳定代码和非稳定代码，稳定代码指的是无论如何不会出错的代码
- 捕获异常是为了处理它，不要捕获了却什么都不处理而抛弃之
- 有 try 块放到了事务代码中，catch 异常后，如果需要回滚事务，一定要注意手动回滚事务
- finally 块必须对资源对象、流对象进行关闭
- 不要在 finally 块中使用 return
- 捕获异常与抛异常，必须是完全匹配，或者捕获异常是抛异常的父类
- 在调用 RPC、二方包、或动态生成类的相关方法时，捕捉异常必须使用 Throwable 类来进行拦截

### 2.2 日志规约

- 应用中不可直接使用日志系统（Log4j、Logback）中的 API，而应依赖使用日志框架 SLF4J 中的 API
- 日志文件推荐至少保存 15 天，因为有些异常具备以"周"为频次发生的特点
- 应用中的扩展日志（如打点、临时监控、访问日志等）命名方式：appName_logType_logName.log
- 对 trace/debug/info 级别的日志输出，必须使用条件输出形式或者使用占位符的方式
- 避免重复打印日志，浪费磁盘空间，务必在日志配置文件中设置 additivity=false
- 异常信息应该包括两类信息：案发现场信息和异常堆栈信息
- 日志打印时禁止直接用 JSON 工具将对象转换成 String

---

## 三、单元测试

- 好的单元测试必须遵守 AIR 原则：
  - **A**utomatic（自动化）
  - **I**ndependent（独立性）
  - **R**epeatable（可重复）
- 单元测试应该是全自动执行的，并且非交互式的
- 单元测试应该是可以重复执行的，不能受到外界环境的影响
- 单元测试应该是可以独立运行的，不依赖于其他测试用例
- 对于单元测试，要保证测试粒度足够小，有助于精确定位问题
- 单元测试的核心准则：用例之间是独立的，不互相依赖
- 单元测试必须可以重复执行，不能受到外界环境的影响
- 对于数据库相关的查询、更新、删除等操作，不能假设数据库里的数据是存在的
- 和数据库相关的单元测试，可以设定自动回滚机制

---

## 四、安全规约

- 隶属于用户个人的页面或者功能必须进行权限控制校验
- 用户敏感数据禁止直接展示，必须对展示数据进行脱敏
- 用户输入的 SQL 参数严格使用参数绑定或者 METADATA 字段值限定
- 用户请求传入的任何参数必须做有效性验证
- 禁止向 HTML 页面输出未经安全过滤或未正确转义的用户数据
- 表单、AJAX 提交必须执行 CSRF 安全验证
- 在使用平台资源，譬如短信、邮件、电话、下单、支付，必须实现正确的防重放的机制

---

## 五、MySQL 数据库

### 5.1 建表规约

- 表达是与否概念的字段，必须使用 is_xxx 的方式命名，数据类型是 unsigned tinyint
- 表名、字段名必须使用小写字母或数字，禁止出现数字开头，禁止两个下划线中间只出现数字
- 表名不使用复数名词
- 禁用保留字，如 desc、range、match、delayed 等
- 主键索引名为 pk_字段名；唯一索引名为 uk_字段名；普通索引名则为 idx_字段名
- 小数类型为 decimal，禁止使用 float 和 double
- 如果存储的字符串长度几乎相等，使用 char 定长字符串类型
- varchar 是可变长字符串，不预先分配存储空间，长度不要超过 5000
- 表必备三字段：id, create_time, update_time
- 表的命名最好是遵循"业务名称_表的作用"

### 5.2 索引规约

- 业务上具有唯一特性的字段，即使是组合字段，也必须建成唯一索引
- 超过三个表禁止 join。需要 join 的字段，数据类型保持绝对一致
- 在 varchar 字段上建立索引时，必须指定索引长度
- 页面搜索严禁左模糊或者全模糊，如果需要请走搜索引擎来解决
- 如果有 order by 的场景，请注意利用索引的有序性
- 利用覆盖索引来进行查询操作，避免回表
- 利用延迟关联或者子查询优化超多分页场景
- SQL 性能优化的目标：至少要达到 range 级别，要求是 ref 级别，如果可以是 consts 最好

### 5.3 SQL 语句

- 不要使用 count(列名) 或 count(常量) 来替代 count(*)
- count(distinct col) 计算该列除 NULL 之外的不重复行数
- 当某一列的值全是 NULL 时，count(col) 的返回结果为 0，但 sum(col) 的返回结果为 NULL
- 使用 ISNULL() 来判断是否为 NULL 值
- 代码中写分页查询逻辑时，若 count 为 0 应直接返回，避免执行后面的分页语句
- 不得使用外键与级联，一切外键概念必须在应用层解决
- 禁止使用存储过程，存储过程难以调试和扩展，更没有移植性
- 数据订正（特别是删除、修改记录操作）时，要先 select，避免出现误删除，确认无误才能执行更新语句
- in 操作能避免则避免，若实在避免不了，需要仔细评估 in 后边的集合元素数量，控制在 1000 个之内

### 5.4 ORM 映射

- 在表查询中，一律不要使用 * 作为查询的字段列表，需要哪些字段必须明确写明
- POJO 类的布尔属性不能加 is，而数据库字段必须加 is_，要求在 resultMap 中进行字段与属性之间的映射
- 不要用 resultClass 当返回参数，即使所有类属性名与数据库字段一一对应，也需要定义 resultMap
- sql.xml 配置参数使用：#{}，#param#，不要使用 ${}，此种方式容易出现 SQL 注入
- iBATIS 自带的 queryForList(String statementName, int start, int size) 不推荐使用
- 不允许直接拿 HashMap 与 Hashtable 作为查询结果集的输出
- 更新数据表记录时，必须同时更新 update_time 字段值为当前时间

---

## 六、工程结构

### 6.1 应用分层

- 开放接口层：可直接封装 Service 方法暴露成 RPC 接口；通过 Web 封装成 http 接口；进行网关安全控制、流量控制等
- 终端显示层：各个端的模板渲染并执行显示的层
- Web 层：主要是对访问控制进行转发，各类基本参数校验，或者不复用的业务简单处理等
- Service 层：相对具体的业务逻辑服务层
- Manager 层：通用业务处理层，有如下特征：
  - 对第三方平台封装的层，预处理返回结果及转化异常信息
  - 对 Service 层通用能力的下沉，如缓存方案、中间件通用处理
  - 与 DAO 层交互，对多个 DAO 的组合复用
- DAO 层：数据访问层，与底层 MySQL、Oracle、Hbase、OB 等进行数据交互
- 外部接口或第三方平台：包括其它部门 RPC 开放接口，基础平台，其它公司的 HTTP 接口

### 6.2 二方库依赖

- 定义 GAV 遵从以下规则：
  - GroupID 格式：com.{公司/BU}.业务线 [.子业务线]，最多 4 级
  - ArtifactID 格式：产品线名-模块名。语义不重复不遗漏
  - Version：详细规定参考下方
- 二方库版本号命名方式：主版本号.次版本号.修订号
- 线上应用不要依赖 SNAPSHOT 版本
- 二方库的新增或升级，保持除功能点之外的其它 jar 包仲裁结果不变
- 二方库里可以定义枚举类型，参数可以使用枚举类型，但是接口返回值不允许使用枚举类型或者包含枚举类型的 POJO 对象

### 6.3 服务器

- 高并发服务器建议调小 TCP 协议的 time_wait 超时时间
- 调大服务器所支持的最大文件句柄数（File Descriptor，简写为 fd）
- 给 JVM 环境参数设置-XX:+HeapDumpOnOutOfMemoryError 参数，让 JVM 碰到 OOM 场景时输出 dump 信息
- 线上生产环境，JVM 的 Xms 和 Xmx 设置一样大小的内存容量，避免在 GC 后调整堆大小带来的压力

---

## 七、设计规约

- 存储方案和底层数据结构的设计获得评审一致通过，并沉淀成为文档
- 在需求分析阶段，如果与系统交互的超过 3 个，使用用例图来表达更加清晰的结构化需求
- 如果某个业务对象的状态超过 3 个，使用状态图来表达并且明确状态变化的各个触发条件
- 系统中超过 2 个对象之间存在协作关系，需要绘制时序图
- 与 2 个系统存在交互关系，需要绘制活动图
- 对模型进行分析时，需要类图和对象图辅助说明
- 确定系统的部署模型，需要部署图辅助说明
- 业务架构设计时，需要业务状态图辅助说明
- 在做系统设计时，需要考虑以下安全因素：
  - 防刷：防止恶意用户通过接口刷数据
  - 防重放：防止请求被截获后重放攻击
  - 防篡改：防止请求参数被篡改

---

**参考**: [阿里巴巴 Java 开发手册（嵩山版）](https://github.com/alibaba/p3c)

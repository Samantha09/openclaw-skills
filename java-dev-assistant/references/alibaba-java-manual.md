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
- 代码中的命名严禁使用拼音与英文混合的方式，更不允许直接使用中文
- 国际通用名称可视同英文：`alibaba / taobao / youku / hangzhou`
- 类名使用 UpperCamelCase，DO / BO / DTO / VO / AO / PO / UID 等除外
- 方法名、参数名、成员变量、局部变量都统一使用 lowerCamelCase
- 常量命名全部大写，单词间用下划线隔开，力求语义表达完整清楚
- 抽象类命名使用 Abstract 或 Base 开头
- 异常类命名使用 Exception 结尾
- 测试类命名以它要测试的类的名称开始，以 Test 结尾
- 数组定义：`String[] args`（中括号是数组类型的一部分），禁止 `String args[]`
- POJO 类中布尔类型的变量，都不要加 is，否则部分框架解析会引起序列化错误
- 包名统一使用小写，点分隔符之间有且仅有一个自然语义的英语单词，包名统一使用单数形式
- 杜绝不规范的缩写，避免望文不知义：禁止 `AbstractClass` 缩写成 `AbsClass`
- 如果使用到了设计模式，建议在类名中体现出具体模式：`OrderFactory` / `LoginProxy` / `ResourceObserver`
- 接口类中的方法和属性不要加任何修饰符号（`public` 也不要加），保持代码简洁
- Service 和 DAO 类：实现类用 Impl 后缀与接口区别
- 枚举类名建议带上 Enum 后缀，枚举成员名称需要全大写，单词间用下划线隔开

**各层命名规约**:

| 层 | 方法前缀 | 说明 |
|------|---------|------|
| Service/DAO | `get` | 获取单个对象 |
| Service/DAO | `list` | 获取多个对象 |
| Service/DAO | `count` | 获取统计值 |
| Service/DAO | `save`/`insert` | 插入 |
| Service/DAO | `remove`/`delete` | 删除 |
| Service/DAO | `update` | 修改 |

**领域模型命名规约**:
- 数据对象：`xxxDO`，xxx 即为数据表名
- 数据传输对象：`xxxDTO`，xxx 为业务领域相关的名称
- 展示对象：`xxxVO`，xxx 一般为网页名称
- POJO 是 DO/DTO/BO/VO 的统称，禁止命名成 `xxxPOJO`

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
- long 或 Long 初始赋值时，使用大写的 L，不能是小写的 l（`Long a = 2l;` 容易与数字 21 混淆）
- 不要使用一个常量类维护所有常量，应该按常量功能进行归类，分开维护
- 常量的复用层次有五层：跨应用共享常量、应用内共享常量、子工程内共享常量、包内共享常量、类内共享常量
- 如果变量值仅在一个范围内变化，且带有名称之外的延伸属性，定义为枚举类

### 1.3 代码格式

- 大括号的使用约定：左大括号前不换行，左大括号后换行，右大括号前换行
- 左小括号和字符之间不出现空格，右小括号和字符之间也不出现空格
- `if/for/while/switch/do` 等保留字与括号之间都必须加空格
- 任何二目、三目运算符的左右两边都需要加一个空格（包括赋值运算符=、逻辑运算符&&、加减乘除符号等）
- 缩进：4 个空格，禁止使用 tab 字符
- 单行字符数限制不超过 120 个，换行时遵循：
  - 第二行相对第一行缩进 4 个空格，从第三行开始不再继续缩进
  - 运算符与下文一起换行
  - 方法调用的点符号与下文一起换行
  - 在多个参数超长时，在逗号后换行
  - 在括号前不要换行
- 方法参数在定义和传入时，多个参数逗号后边必须加空格
- IDE 的 text file encoding 设置为 UTF-8；换行符使用 Unix 格式
- 没有必要增加若干空格来使某一行的字符与上一行对应位置的字符对齐
- 方法体内的执行语句组、变量的定义语句组、不同的业务逻辑之间插入一个空行，相同业务逻辑和语义之间不需要插入空行

### 1.4 OOP 规约

- 避免通过一个类的对象引用访问此类的静态变量或静态方法，直接用类名来访问即可
- 所有的覆写方法，必须加 @Override 注解
- 相同参数类型，相同业务含义，才可以使用 Java 的可变参数，避免使用 Object
- 外部正在调用或者二方库依赖的接口，不允许修改方法签名，接口过时必须加 @Deprecated 注解
- 不能使用过时的类或方法
- Object 的 equals 方法容易抛空指针异常，应使用常量或确定有值的对象来调用 equals（推荐 `java.util.Objects#equals`）
- 所有的相同类型的包装类对象之间值的比较，全部使用 equals 方法比较（Integer 在 -128 至 127 范围内复用缓存对象，范围之外必须用 equals）
- 关于基本数据类型与包装数据类型的使用标准如下：
  - 【强制】所有的 POJO 类属性必须使用包装数据类型
  - 【强制】RPC 方法的返回值和参数必须使用包装数据类型
  - 【推荐】所有的局部变量使用基本数据类型
- 定义 DO/DTO/VO 等 POJO 类时，不要设定任何属性默认值
- 序列化类新增属性时，请不要修改 serialVersionUID 字段
- 构造方法里面禁止加入任何业务逻辑，如果有初始化逻辑，请放在 init 方法中
- POJO 类必须写 toString 方法，如果继承了另一个 POJO 类，注意加 `super.toString`
- 使用索引访问 String 的 split 方法得到的数组时，需做最后一个分隔符后有无内容的检查
- 当一个类有多个构造方法或多个同名方法，应按顺序放置在一起，便于阅读
- 类内方法定义顺序依次是：公有方法或保护方法 > 私有方法 > getter/setter 方法
- setter 方法中，参数名称与类成员变量名称一致（`this.成员名 = 参数名`），getter/setter 方法中不要增加业务逻辑
- 循环体内，字符串的连接方式使用 StringBuilder 的 append 方法
- final 关键字使用场景：
  - 不允许被继承的类
  - 不允许修改引用的域对象（如 POJO 类的域变量）
  - 不允许被重写的方法（如 POJO 类的 setter 方法）
  - 不允许运行过程中重新赋值的局部变量
  - 避免上下文重复使用一个变量
- 慎用 Object 的 clone 方法来拷贝对象（默认是浅拷贝）
- 类成员与方法访问控制从严：
  - 不允许外部直接通过 new 来创建对象，构造方法必须是 private
  - 工具类不允许有 public 或 default 构造方法
  - 类非 static 成员变量且仅在本类使用，必须是 private
  - 类 static 成员变量如果仅在本类使用，必须是 private
  - 若是 static 成员变量，必须考虑是否为 final
  - 类成员方法只供类内部调用，必须是 private
  - 类成员方法只对继承类公开，限制为 protected

### 1.5 集合处理

- 关于 hashCode 和 equals 的处理，遵循如下规则：
  - 只要重写 equals，就必须重写 hashCode
  - Set 存储的是不重复的对象，依据 hashCode 和 equals 进行判断
  - 如果自定义对象作为 Map 的键，那么必须重写 hashCode 和 equals
- ArrayList 的 subList 结果不可强转成 ArrayList
- 在 subList 场景中，高度注意对原集合元素个数的修改，会导致子列表的遍历、增加、删除均产生 ConcurrentModificationException
- 使用集合转数组的方法，必须使用集合的 toArray(T[] array)
- 使用工具类 Arrays.asList() 把数组转换成集合时，不能使用其修改集合相关的方法（add/remove/clear 会抛 UnsupportedOperationException）
- 泛型通配符：`<? extends T>` 不能使用 add 方法，`<? super T>` 不能使用 get 方法（PECS 原则）
- 不要在 foreach 循环里进行元素的 remove/add 操作，应使用 Iterator 方式
- 在 JDK 7 版本及以上，Comparator 要满足自反性、传递性、对称性
- 集合初始化时，指定集合初始值大小（`initialCapacity = (需要存储的元素个数 / 负载因子) + 1`）
- 使用 entrySet 遍历 Map 类集合 KV，而不是 keySet 方式（keySet 遍历了 2 次）；JDK8 使用 Map.forEach
- 高度注意 Map 类集合 K/V 能不能存储 null 值：ConcurrentHashMap 不允许 null，HashMap 允许 null
- 利用 Set 元素唯一的特性，快速对一个集合进行去重操作，避免使用 List 的 contains 方法

### 1.6 并发处理

- 获取单例对象需要保证线程安全，其中的方法也要保证线程安全
- 创建线程或线程池时请指定有意义的线程名称，方便出错时回溯
- 线程资源必须通过线程池提供，不允许在应用中自行显式创建线程
- 线程池不允许使用 Executors 去创建，而是通过 ThreadPoolExecutor 的方式（规避 OOM 风险）
- SimpleDateFormat 是线程不安全的类，一般不要定义为 static 变量；JDK8 推荐 DateTimeFormatter
- 高并发时，同步调用应该去考量锁的性能损耗：能用无锁数据结构就不用锁，能锁区块就不锁整个方法体，能用对象锁就不用类锁
- 对多个资源、数据库表、对象同时加锁时，需要保持一致的加锁顺序，否则可能死锁
- 并发修改同一记录时，避免更新丢失需要加锁；冲突概率 < 20% 推荐乐观锁，乐观锁重试次数不得小于 3 次
- 多线程并行处理定时任务时，使用 ScheduledExecutorService 替代 Timer（Timer 的一个任务异常会导致其它任务终止）
- 使用 CountDownLatch 进行异步转同步时，线程执行代码注意 catch 异常，确保 countDown 方法可以执行
- 避免 Random 实例被多线程使用，JDK7+ 直接使用 ThreadLocalRandom
- 双重检查锁实现延迟初始化时，目标属性必须声明为 volatile
- volatile 解决多线程内存不可见问题，但对于多写无法解决线程安全；count++ 使用 AtomicInteger，JDK8 推荐 LongAdder（比 AtomicLong 性能更好）
- 在容量不够进行 resize 时由于高并发可能出现死链，导致 CPU 飙升
- ThreadLocal 无法解决共享对象的更新问题，ThreadLocal 对象建议使用 static 修饰

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

- 在一个 switch 块内，每个 case 要么通过 break/return 等来终止，要么注释说明程序将继续执行到哪一个 case 为止；必须包含一个 default 语句
- 当 switch 括号内的变量类型为 String 并且此变量为外部参数时，必须先进行 null 判断
- 在 if/else/for/while/do 语句中必须使用大括号，即使只有一行代码
- 表达异常的分支时，少用 if-else 方式，改写成卫语句（guard clause）
- if-else 超过 3 层必须使用卫语句、策略模式或状态模式
- 除常用方法（如 getXxx/isXxx）外，不要在条件判断中执行复杂的语句，将复杂逻辑判断的结果赋值给一个有意义的布尔变量名
- 循环体中的语句要考量性能，以下操作尽量移至循环体外：定义对象、变量、获取数据库连接、不必要的 try-catch
- 接口入参保护，常见于批量操作接口
- 参数校验时机：调用频次低的方法、执行时间开销大的方法、需要高稳定性的方法、对外开放接口、敏感权限入口必须校验
- 不需要参数校验：极可能被循环调用的方法（需在方法说明中注明外部参数检查要求）、底层调用频度高的方法、private 方法且能确定调用方已校验

### 1.8 注释规约

- 类、类属性、类方法的注释必须使用 Javadoc 规范（`/** 内容 */`），不得使用 `//xxx` 方式
- 所有的抽象方法（包括接口中的方法）必须要用 Javadoc 注释，包括返回值、参数、异常说明，以及该方法做什么
- 所有的类都必须添加创建者和创建日期
- 方法内部单行注释，在被注释语句上方另起一行，使用 `//` 注释
- 方法内部多行注释使用 `/* */` 注释，注意与代码对齐
- 所有的枚举类型字段必须要有注释，说明每个数据项的用途
- 与其"半吊子"英文来注释，不如用中文注释把问题说清楚，专有名词与关键字保持英文原文
- 代码修改的同时，注释也要进行相应的修改，尤其是参数、返回值、异常、核心逻辑
- 合理处理注释掉的代码：在上方详细说明，如果无用则删除（代码仓库保存了历史代码）
- 好的命名、代码结构是自解释的，注释力求精简准确、表达到位，避免过多过滥
- 特殊注释标记需注明标记人与标记时间：
  - TODO: (标记人，标记时间，[预计处理时间])
  - FIXME: (标记人，标记时间，[预计处理时间])

---

## 二、异常日志

### 1.9 其他

- 在使用正则表达式时，利用好其预编译功能：不要在方法体内定义 `Pattern pattern = Pattern.compile(规则)`
- 注意 Math.random() 返回 double 类型，取值范围 0≤x<1，获取整数随机数使用 Random 的 nextInt/nextLong
- 获取当前毫秒数使用 `System.currentTimeMillis()`，而不是 `new Date().getTime()`；JDK8 推荐 Instant 类
- 不要在视图模板中加入任何复杂的逻辑
- 任何数据结构的构造或初始化，都应指定大小，避免数据结构无限增长吃光内存
- 对于"明确停止使用的代码和配置"要坚决从程序中清理出去，避免造成过多垃圾

---

## 二、异常日志

### 2.1 异常处理

- Java 类库中定义的可以通过预检查方式规避的 RuntimeException 异常不应该通过 catch 的方式来处理（如 IndexOutOfBoundsException、NullPointerException）
- 异常不要用来做流程控制，条件控制
- catch 时请分清稳定代码和非稳定代码，稳定代码指的是无论如何不会出错的代码
- 捕获异常是为了处理它，不要捕获了却什么都不处理而抛弃之
- 有 try 块放到了事务代码中，catch 异常后，如果需要回滚事务，一定要注意手动回滚事务
- finally 块必须对资源对象、流对象进行关闭（JDK7+ 使用 try-with-resources）
- 不要在 finally 块中使用 return
- 捕获异常与抛异常，必须是完全匹配，或者捕获异常是抛异常的父类
- 在调用 RPC、二方包、或动态生成类的相关方法时，捕捉异常必须使用 Throwable 类来进行拦截
- 方法的返回值可以为 null，必须添加注释充分说明什么情况下会返回 null
- 防止 NPE 是程序员的基本修养，注意以下场景：
  - 返回类型为基本数据类型，return 包装数据类型对象时自动拆箱
  - 数据库查询结果可能为 null
  - 集合里的元素即使 isNotEmpty，取出的数据元素也可能为 null
  - 远程调用返回对象时，一律要求进行空指针判断
  - Session 中获取的数据建议 NPE 检查
  - 级联调用 obj.getA().getB().getC() 易产生 NPE
  - 推荐 JDK8 的 Optional 类防止 NPE
- 定义时区分 unchecked/checked 异常，应使用有业务含义的自定义异常（如 DAOException / ServiceException）
- 代码中使用"抛异常"还是"返回错误码"：对外 HTTP/API 必须使用错误码；应用内部推荐异常抛出；跨应用 RPC 优先 Result 方式
- 遵循 DRY 原则（Don't Repeat Yourself），必要时抽取共性方法或抽象公共类

### 2.2 日志规约

- 应用中不可直接使用日志系统（Log4j、Logback）中的 API，而应依赖使用日志框架 SLF4J 中的 API
- 日志文件推荐至少保存 15 天，因为有些异常具备以"周"为频次发生的特点
- 应用中的扩展日志命名方式：appName_logType_logName.log
- 对 trace/debug/info 级别的日志输出，必须使用条件输出形式或者使用占位符的方式
- 避免重复打印日志，务必在日志配置文件中设置 additivity=false
- 异常信息应该包括两类信息：案发现场信息和异常堆栈信息
- 日志打印时禁止直接用 JSON 工具将对象转换成 String
- 谨慎地记录日志：生产环境禁止输出 debug 日志，有选择地输出 info 日志
- 可以使用 warn 日志级别记录用户输入参数错误，error 级别只记录系统逻辑出错、异常等重要错误

### 2.3 分层异常处理规约

- **DAO 层**：使用 catch(Exception e) 并 throw new DAOException(e)，不需要打印日志
- **Service 层**：出现异常时必须记录出错日志到磁盘，尽可能带上参数信息
- **Manager 层**：与 Service 同机部署时同 DAO 处理方式，单独部署时同 Service
- **Web 层**：不应该继续往上抛异常，直接跳转到友好错误页面
- **开放接口层**：将异常处理成错误码和错误信息方式返回

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

**分层领域模型规约**:
- **DO (Data Object)**：与数据库表结构一一对应，通过 DAO 层向上传输数据源对象
- **DTO (Data Transfer Object)**：数据传输对象，Service 和 Manager 向外传输的对象
- **BO (Business Object)**：业务对象，可以由 Service 层输出的封装业务逻辑的对象
- **Query**：数据查询对象，各层接收上层的查询请求（超过 2 个参数的查询封装，禁止使用 Map）
- **VO (View Object)**：显示层对象，通常是 Web 向模板渲染引擎层传输的对象

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

- 高并发服务器建议调小 TCP 协议的 time_wait 超时时间（linux: `net.ipv4.tcp_fin_timeout = 30`）
- 调大服务器所支持的最大文件句柄数（File Descriptor，简写为 fd）
- 给 JVM 环境参数设置-XX:+HeapDumpOnOutOfMemoryError 参数，让 JVM 碰到 OOM 场景时输出 dump 信息
- 线上生产环境，JVM 的 Xms 和 Xmx 设置一样大小的内存容量，避免在 GC 后调整堆大小带来的压力
- 服务器内部重定向使用 forward；外部重定向地址使用 URL 拼装工具类

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

# Java 常见陷阱与反模式

## 1. 空指针异常（NPE）

### 1.1 使用对象调用 equals
```java
// 坏
if (userName.equals("admin")) { ... }

// 好
if ("admin".equals(userName)) { ... }
// 或
if (Objects.equals(userName, "admin")) { ... }
```

### 1.2 自动拆箱
```java
// 坏：可能 NPE
int count = Integer.valueOf(request.getParameter("count"));

// 好
Integer countObj = Integer.valueOf(request.getParameter("count"));
int count = (countObj != null) ? countObj : 0;
```

### 1.3 Optional 误用
```java
// 坏
Optional<User> userOpt = ...;
if (userOpt.isPresent()) { return userOpt.get(); }

// 好
return userOpt.orElse(null);
// 或
return userOpt.orElseThrow(() -> new RuntimeException("User not found"));
// 实际项目中建议抛出具体的自定义业务异常
```

---

## 2. 集合处理

### 2.1 foreach 中修改集合
```java
// 坏：ConcurrentModificationException
for (Item item : list) {
    if (item.isExpired()) list.remove(item);
}

// 好
list.removeIf(Item::isExpired);
// 或显式使用 Iterator
```

### 2.2 Arrays.asList 的陷阱
```java
// 坏：UnsupportedOperationException
List<String> list = Arrays.asList("a", "b");
list.add("c");

// 好
List<String> list = new ArrayList<>(Arrays.asList("a", "b"));
```

### 2.3 subList 强转
```java
// 坏
List<String> sub = (ArrayList<String>) list.subList(0, 5);

// 好
List<String> sub = new ArrayList<>(list.subList(0, 5));
```

---

## 3. 并发问题

### 3.1 使用 Executors 创建线程池
```java
// 坏：无界队列可能导致 OOM
ExecutorService executor = Executors.newFixedThreadPool(10);

// 好：使用 ThreadPoolExecutor 显式指定参数
ThreadFactory namedThreadFactory = r -> {
    Thread t = new Thread(r);
    t.setName("biz-pool-" + t.getId());
    return t;
};
new ThreadPoolExecutor(
    4, 8, 60L, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(100),
    namedThreadFactory,
    new ThreadPoolExecutor.CallerRunsPolicy()
);
```

### 3.2 SimpleDateFormat 共享
```java
// 坏：线程不安全
private static final SimpleDateFormat SDF = new SimpleDateFormat("yyyy-MM-dd");

// 好
private static final DateTimeFormatter DTF = DateTimeFormatter.ofPattern("yyyy-MM-dd");
```

### 3.3 双检锁未用 volatile
```java
// 坏：指令重排序导致半初始化对象
private static Singleton instance;

// 好
private static volatile Singleton instance;
```

---

## 4. 异常处理

### 4.1 捕获 Throwable / Exception
```java
// 坏：可能吞掉 Error
} catch (Exception e) { ... }

// 好：只捕获可恢复的具体异常
} catch (IllegalStateException e) { ... }
// 实际项目中建议使用项目自定义的业务异常
```

### 4.2 吞掉异常
```java
// 坏
try { ... } catch (IOException e) { }

// 好
try { ... } catch (IOException e) {
    log.error("读取文件失败, path={}", path, e);
    throw new RuntimeException("读取文件失败", e);
}
// 实际项目中建议包装为项目自定义的业务异常再抛出
```

### 4.3 异常用作流程控制
```java
// 坏：性能差，可读性差
try {
    return Integer.parseInt(str);
} catch (NumberFormatException e) {
    return 0;
}

// 好：先校验再转换
if (str != null && str.matches("\\d+")) {
    return Integer.parseInt(str);
}
return 0;
```

---

## 5. 资源释放

### 5.1 未关闭资源
```java
// 坏
InputStream is = new FileInputStream(file);
...
// 可能未关闭

// 好
try (InputStream is = new FileInputStream(file)) {
    ...
}
```

---

## 6. 性能反模式

### 6.1 循环内字符串拼接
```java
// 坏
String result = "";
for (String s : list) {
    result += s;
}

// 好
StringBuilder sb = new StringBuilder();
for (String s : list) {
    sb.append(s);
}
```

### 6.2 不当使用正则
```java
// 坏：每次编译正则
if (str.matches("^\\d+$")) { ... }

// 好
private static final Pattern DIGIT_PATTERN = Pattern.compile("^\\d+$");
if (DIGIT_PATTERN.matcher(str).matches()) { ... }
```

### 6.3 创建不必要的对象
```java
// 坏
Long sum = 0L;
for (long i = 0; i < Integer.MAX_VALUE; i++) {
    sum += i; // 大量自动装箱
}

// 好
long sum = 0L;
for (long i = 0; i < Integer.MAX_VALUE; i++) {
    sum += i;
}
```

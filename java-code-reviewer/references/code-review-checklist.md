# 代码审查检查清单

## 通用原则

1. 审查前先理解需求/设计目标
2. 关注正确性优先于风格
3. 区分阻塞级、警告级和建议级
4. 评论要具体、可执行、有依据

---

## 一、规范与风格

| 检查项 | 级别 | 说明 |
|--------|------|------|
| 命名符合规范（类/方法/变量/常量） | WARNING | UpperCamelCase / lowerCamelCase / UPPER_SNAKE_CASE |
| 未使用通配符导入 | WARNING | 逐条导入，分组有序 |
| 无魔法值 | WARNING | 常量应显式定义 |
| 行长度 ≤ 120 | SUGGESTION | 过长行应合理断行 |
| 使用 4 空格缩进，无 Tab | WARNING | |
| 左大括号在同一行 | SUGGESTION | 统一风格 |
| 类和方法有必要的 Javadoc | SUGGESTION | 公共 API 必须注释 |

---

## 二、正确性与健壮性

| 检查项 | 级别 | 说明 |
|--------|------|------|
| 空指针风险 | BLOCKER | `Object.equals()`、拆箱、链式调用 |
| 边界条件处理 | BLOCKER | 数组越界、除零、空集合 |
| 异常捕获合理 | WARNING | 不捕获 `Throwable`，不吞异常 |
| 资源释放（流、连接、锁） | BLOCKER | try-with-resources 或 finally |
| 并发安全 | BLOCKER | 共享可变状态、线程池、锁顺序 |
| 重写了 `equals` 是否重写 `hashCode` | WARNING | |
| 避免浮点数比较相等 | WARNING | 使用误差范围 |

---

## 三、性能与效率

| 检查项 | 级别 | 说明 |
|--------|------|------|
| 循环内避免重复计算/查询 | WARNING | 提取到循环外 |
| 合理选择集合类型 | SUGGESTION | List/Set/Map 场景匹配 |
| 避免在循环中进行字符串拼接 | SUGGESTION | 优先 StringBuilder |
| 数据库 N+1 查询 | BLOCKER | 批量查询、Join、懒加载 |
| 大对象/大集合处理 | WARNING | 分页、流式处理 |

---

## 四、安全性

| 检查项 | 级别 | 说明 |
|--------|------|------|
| SQL 注入风险 | BLOCKER | 预编译语句、参数化查询 |
| 硬编码敏感信息 | BLOCKER | 密码、密钥、Token |
| 输入校验 | WARNING | 白名单校验、长度限制 |
| 反序列化安全 | BLOCKER | 不信任的数据反序列化 |
| 越权/权限校验 | BLOCKER | 接口级别和方法级别鉴权 |
| XSS 风险 | WARNING | 输出编码、富文本过滤 |

---

## 五、可维护性与设计

| 检查项 | 级别 | 说明 |
|--------|------|------|
| 方法长度 ≤ 50 行 | SUGGESTION | 过长应拆分 |
| 圈复杂度过高 | WARNING | 考虑卫语句、策略模式 |
| 重复代码 | WARNING | 提取公共方法 |
| 死代码/未使用导入 | SUGGESTION | 及时清理 |
| 硬编码业务逻辑 | WARNING | 配置化、策略化 |
| 单一职责原则 | SUGGESTION | 类和方法职责清晰 |

---

## 六、测试

| 检查项 | 级别 | 说明 |
|--------|------|------|
| 变更是否伴随测试 | WARNING | Bug 修复和功能新增必须有测试 |
| 测试命名清晰 | SUGGESTION | `方法_场景_预期结果` |
| 覆盖边界和异常 | WARNING | null、空集合、异常分支 |
| 无过度 Mock | SUGGESTION | 验证行为而非实现细节 |

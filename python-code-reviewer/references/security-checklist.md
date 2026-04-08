# Python 安全审查清单

## 输入验证

- [ ] 用户输入是否经过验证和清洗
- [ ] 文件路径是否做了路径遍历检查（`../`）
- [ ] 数值参数是否检查了范围（防止负数、溢出）
- [ ] 字符串长度是否有限制

## 注入攻击

### SQL 注入

```python
# 错误！SQL 拼接
query = f"SELECT * FROM users WHERE name = '{name}'"

# 正确：参数化查询
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

### 命令注入

```python
# 错误！
os.system(f"ping {user_input}")
subprocess.run(f"cat {filename}", shell=True)

# 正确
subprocess.run(["ping", user_input])  # 不用 shell=True
subprocess.run(["cat", filename])
```

### 代码注入

```python
# 错误！
eval(user_input)
exec(user_string)

# 正确：避免 eval/exec，用安全的替代方案
# 如 json.loads 替代 eval 解析 JSON
import json
data = json.loads(user_input)
```

## 敏感信息

- [ ] 无硬编码密码、API Key、Token
- [ ] 敏感信息通过环境变量或配置文件读取
- [ ] 日志中不记录密码、Token 等敏感数据
- [ ] 异常信息不泄露内部路径、堆栈细节（生产环境）
- [ ] .gitignore 包含 .env、credentials 等文件

```python
# 错误！日志中泄露信息
logging.info(f"Login with password: {password}")

# 正确
logging.info(f"User {username} login attempt")
```

## 文件操作

- [ ] 文件路径做了校验，防止路径遍历
- [ ] 上传文件有类型和大小限制
- [ ] 临时文件使用 `tempfile` 模块

```python
# 路径遍历防护
import os
def safe_path(base_dir, filename):
    filepath = os.path.join(base_dir, filename)
    if not os.path.realpath(filepath).startswith(os.path.realpath(base_dir)):
        raise ValueError("Invalid path")
    return filepath
```

## 反序列化

```python
# 错误！pickle 可执行任意代码
import pickle
data = pickle.loads(untrusted_input)

# 正确：使用 json 或限制 unpickle
import json
data = json.loads(untrusted_input)
```

## 依赖安全

- [ ] 定期更新依赖，修复已知漏洞
- [ ] 使用 `pip audit` 或 `safety` 检查依赖漏洞
- [ ] 锁定依赖版本（requirements.txt 或 poetry.lock）

## 网络

- [ ] HTTP 请求使用 HTTPS
- [ ] SSL 证书验证未禁用（`verify=False`）
- [ ] 请求有超时设置
- [ ] 不盲目跟随重定向

```python
# 错误
requests.get(url, verify=False, timeout=None)

# 正确
requests.get(url, verify=True, timeout=10)
```

## 认证与授权

- [ ] 密码使用 bcrypt/scrypt 哈希存储
- [ ] Session Token 使用安全随机数生成
- [ ] 敏感操作需要重新认证
- [ ] API 端点有权限检查

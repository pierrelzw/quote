# Quote Web - Python Backend

这是一个名言网站的Python Flask后端，用于替代原来的Node.js后端。

## 技术栈

- **Python 3.12**
- **Flask 3.1.1** - 轻量级Web框架
- **Flask-CORS** - 跨域资源共享
- **Flask-JWT-Extended** - JWT认证
- **bcrypt** - 密码加密
- **SQLite** - 数据库

## 功能特性

1. **用户认证**
   - 用户注册
   - 用户登录
   - JWT token认证

2. **名言管理**
   - 获取名言列表（支持分页）
   - 添加新名言（需要登录）
   - 数据库初始化和种子数据

## 🚀 快速开始

### 方法 1: 一键启动 (推荐)
```bash
./quick_start.sh
```

### 方法 2: 手动启动
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python database.py

# 3. 启动服务器
python app.py
```

服务器将在 `http://localhost:3001` 启动。

## 🧪 运行测试

```bash
# 运行所有测试
./run_tests.sh

# 查看测试状态
./test_dashboard.sh
```

## API 端点

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

### 名言相关
- `GET /api/quotes` - 获取名言列表（支持分页）
- `POST /api/quotes` - 添加名言（需要认证）

## 数据库结构

### users 表
- id (INTEGER PRIMARY KEY)
- username (TEXT UNIQUE)
- password (TEXT)
- created_at (DATETIME)

### quotes 表
- id (INTEGER PRIMARY KEY)
- content (TEXT)
- author (TEXT)
- user_id (INTEGER, 外键)
- created_at (DATETIME)

## 与原Node.js后端的对比

### 优势
- **更简洁的代码**: Python的语法更加简洁易读
- **更好的生态系统**: Flask生态系统丰富，插件众多
- **更好的维护性**: Python代码更容易维护和扩展
- **更强的可读性**: 代码结构清晰，易于理解

### 兼容性
- 完全兼容现有的前端代码
- API接口保持一致
- 数据库结构相同
- 认证机制兼容

## 测试

```bash
# 测试服务器状态
curl http://localhost:3001/

# 测试用户注册
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'

# 测试用户登录
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'

# 测试获取名言
curl "http://localhost:3001/api/quotes?page=1&pageSize=5"
```

## 部署注意事项

1. 在生产环境中，请修改 `JWT_SECRET_KEY` 为安全的密钥
2. 使用 Gunicorn 或 uWSGI 等 WSGI 服务器
3. 配置合适的数据库连接池
4. 启用 HTTPS

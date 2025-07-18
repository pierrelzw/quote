# 🚀 Quote Web Python 后端 - 运行指南

## 📋 项目概述

这是一个基于 Python Flask 的名言网站后端，提供用户认证和名言管理功能。

## 🏗️ 系统要求

- **Python**: 3.8+ (推荐 3.12)
- **操作系统**: macOS, Linux, Windows
- **内存**: 至少 512MB 可用内存
- **磁盘空间**: 至少 100MB 可用空间

## 📦 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd quote-web/backend-python
```

### 2. 安装依赖
```bash
# 安装应用依赖
pip install -r requirements.txt

# 安装测试依赖 (可选)
pip install -r test_requirements.txt
```

### 3. 初始化数据库
```bash
python database.py
```

### 4. 启动服务器
```bash
python app.py
```

🎉 **服务器将在 `http://localhost:3001` 启动**

## 🔧 详细安装步骤

### 方法 1: 使用虚拟环境 (推荐)

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\\Scripts\\activate

# 安装依赖
pip install -r requirements.txt
pip install -r test_requirements.txt

# 初始化数据库
python database.py

# 启动服务器
python app.py
```

### 方法 2: 使用系统 Python

```bash
# 直接安装依赖
pip install -r requirements.txt

# 初始化数据库
python database.py

# 启动服务器
python app.py
```

### 方法 3: 使用 conda

```bash
# 创建 conda 环境
conda create -n quote-web python=3.12

# 激活环境
conda activate quote-web

# 安装依赖
pip install -r requirements.txt
pip install -r test_requirements.txt

# 初始化数据库
python database.py

# 启动服务器
python app.py
```

## 🧪 运行测试

### 快速测试
```bash
# 运行所有测试
./run_tests.sh

# 或者使用 pytest
pytest

# 查看测试仪表板
./test_dashboard.sh
```

### 详细测试选项
```bash
# 运行特定类型的测试
./run_tests.sh unit          # 单元测试
./run_tests.sh integration   # 集成测试
./run_tests.sh security      # 安全测试
./run_tests.sh performance   # 性能测试

# 生成覆盖率报告
./run_tests.sh coverage
```

## 🌐 API 测试

### 测试根端点
```bash
curl http://localhost:3001/
```

### 测试用户注册
```bash
curl -X POST http://localhost:3001/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{"username": "testuser", "password": "testpass123"}'
```

### 测试用户登录
```bash
curl -X POST http://localhost:3001/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username": "testuser", "password": "testpass123"}'
```

### 测试获取名言
```bash
curl "http://localhost:3001/api/quotes?page=1&pageSize=5"
```

## 📁 项目结构

```
backend-python/
├── app.py                  # 主应用文件
├── database.py             # 数据库初始化
├── production.py           # 生产环境配置
├── requirements.txt        # 应用依赖
├── test_requirements.txt   # 测试依赖
├── pytest.ini             # 测试配置
├── run_tests.sh           # 测试脚本
├── test_dashboard.sh      # 测试仪表板
├── db/                    # 数据库文件
│   └── quote.db
├── tests/                 # 测试文件
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_security.py
│   ├── test_performance.py
│   └── test_edge_cases.py
└── docs/                  # 文档
    ├── README.md
    ├── TESTING_GUIDE.md
    └── PROJECT_STRUCTURE.md
```

## 🎯 API 端点

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

### 名言相关
- `GET /api/quotes` - 获取名言列表（支持分页）
- `POST /api/quotes` - 添加名言（需要认证）

### 分页参数
- `page`: 页码（默认：1）
- `pageSize`: 每页数量（默认：10）

## 🔒 认证说明

### 获取 JWT Token
```bash
# 1. 注册用户
response=$(curl -s -X POST http://localhost:3001/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{"username": "myuser", "password": "mypass123"}')

# 2. 登录获取 token
response=$(curl -s -X POST http://localhost:3001/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username": "myuser", "password": "mypass123"}')

# 3. 提取 token
token=$(echo $response | python -c "import sys, json; print(json.load(sys.stdin)['token'])")
```

### 使用 Token 添加名言
```bash
curl -X POST http://localhost:3001/api/quotes \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $token" \\
  -d '{"content": "人生苦短，我用Python", "author": "程序员"}'
```

## 🚀 生产环境部署

### 使用 Gunicorn
```bash
# 安装 Gunicorn
pip install gunicorn

# 启动生产服务器
gunicorn -w 4 -b 0.0.0.0:3001 production:app
```

### 使用 uWSGI
```bash
# 安装 uWSGI
pip install uwsgi

# 启动服务器
uwsgi --http :3001 --module production:app --processes 4
```

### 环境变量配置
```bash
# 设置生产环境变量
export FLASK_ENV=production
export JWT_SECRET_KEY=your-super-secret-key-here
export DATABASE_URL=sqlite:///production.db
```

## 🛠️ 常见问题解决

### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :3001

# 终止进程
kill -9 <PID>

# 或者使用不同端口
export PORT=3002
python app.py
```

### 2. 数据库文件权限问题
```bash
# 检查数据库文件权限
ls -la db/quote.db

# 修改权限
chmod 664 db/quote.db
```

### 3. 依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 4. 测试失败
```bash
# 清理测试缓存
rm -rf .pytest_cache
rm -rf __pycache__

# 重新运行测试
pytest --cache-clear
```

## 📊 开发工具

### 查看测试状态
```bash
./test_dashboard.sh
```

### 运行特定测试
```bash
# 运行单个测试文件
pytest tests/test_api.py -v

# 运行单个测试方法
pytest tests/test_api.py::TestAPI::test_register_success -v
```

### 生成测试覆盖率报告
```bash
pytest --cov=app --cov=database --cov-report=html
open htmlcov/index.html
```

## 🔍 调试技巧

### 启用调试模式
```bash
export FLASK_DEBUG=1
python app.py
```

### 查看日志
```bash
# 实时查看日志
tail -f app.log
```

### 数据库检查
```bash
# 使用 SQLite 命令行
sqlite3 db/quote.db
.tables
.schema users
.schema quotes
SELECT * FROM users;
```

## 📝 开发建议

1. **使用虚拟环境**: 避免依赖冲突
2. **运行测试**: 确保代码质量
3. **查看文档**: 详细信息请参考 `docs/` 目录
4. **定期备份**: 数据库文件很重要

## 🆘 获取帮助

- **测试指南**: `docs/TESTING_GUIDE.md`
- **项目结构**: `docs/PROJECT_STRUCTURE.md`
- **API 文档**: 查看代码注释
- **测试仪表板**: `./test_dashboard.sh`

---

**🎉 祝您使用愉快！如有问题，请参考文档或提交 Issue。**

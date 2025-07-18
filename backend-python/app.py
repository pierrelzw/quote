"""
Quote API - 统一的 Flask 应用
支持开发环境（SQLite）和生产环境（PostgreSQL）
通过环境变量自动适配
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import sqlite3
import bcrypt
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 基础配置
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev_jwt_secret_key_change_in_production')
jwt = JWTManager(app)

# CORS 配置 - 根据环境自动调整
def setup_cors():
    cors_origins = os.getenv('CORS_ORIGINS', '*')
    if cors_origins == '*':
        CORS(app)
        print("CORS: 允许所有来源 (开发模式)")
    else:
        CORS(app, origins=cors_origins.split(','))
        print(f"CORS: 限制来源 {cors_origins}")

setup_cors()

# 数据库配置 - 自动检测环境
DATABASE_URL = os.getenv('DATABASE_URL')
IS_PRODUCTION = DATABASE_URL and DATABASE_URL.startswith('postgresql://')

if IS_PRODUCTION:
    print("🚀 生产环境模式: 使用 PostgreSQL")
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    def get_db_connection():
        return psycopg2.connect(DATABASE_URL)
        
    def init_database():
        """初始化 PostgreSQL 数据库"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建名言表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quotes (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    user_id INTEGER REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ PostgreSQL 数据库初始化完成")
        except Exception as e:
            print(f"❌ PostgreSQL 数据库初始化失败: {e}")
            raise
            
    def execute_query(query, params=None, fetch_one=False, fetch_all=False):
        """执行 PostgreSQL 查询"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = None
                
            conn.commit()
            return result
        finally:
            conn.close()
            
else:
    print("🔧 开发环境模式: 使用 SQLite")
    db_path = os.getenv('DATABASE_PATH', './db/quote.db')
    
    def get_db_connection():
        # 确保数据库目录存在
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"📁 创建数据库目录: {db_dir}")
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def init_database():
        """初始化 SQLite 数据库"""
        try:
            conn = get_db_connection()
            
            # 创建用户表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建名言表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    author TEXT NOT NULL,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ SQLite 数据库初始化完成")
        except Exception as e:
            print(f"❌ SQLite 数据库初始化失败: {e}")
            raise
            
    def execute_query(query, params=None, fetch_one=False, fetch_all=False):
        """执行 SQLite 查询"""
        conn = get_db_connection()
        try:
            if fetch_one:
                result = conn.execute(query, params or ()).fetchone()
            elif fetch_all:
                result = conn.execute(query, params or ()).fetchall()
            else:
                conn.execute(query, params or ())
                result = None
                
            conn.commit()
            return result
        finally:
            conn.close()

# 健康检查
@app.route('/health')
def health_check():
    return {
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'environment': 'production' if IS_PRODUCTION else 'development',
        'database': 'PostgreSQL' if IS_PRODUCTION else 'SQLite'
    }

@app.route('/')
def index():
    return {
        'message': 'Quote API is running (Python Flask)!',
        'version': '2.0.0',
        'environment': 'production' if IS_PRODUCTION else 'development'
    }

# 用户认证路由
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username') if data.get('username') is not None else ''
    password = data.get('password') if data.get('password') is not None else ''
    
    username = username.strip() if isinstance(username, str) else ''
    password = password.strip() if isinstance(password, str) else ''
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    try:
        # 检查用户是否存在
        if IS_PRODUCTION:
            existing_user = execute_query(
                'SELECT id FROM users WHERE username = %s', 
                (username,), 
                fetch_one=True
            )
        else:
            existing_user = execute_query(
                'SELECT id FROM users WHERE username = ?', 
                (username,), 
                fetch_one=True
            )
            
        if existing_user:
            return jsonify({'message': '用户已存在'}), 400
            
        # 创建用户
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        if IS_PRODUCTION:
            execute_query(
                'INSERT INTO users (username, password) VALUES (%s, %s)',
                (username, hashed_password.decode('utf-8'))
            )
        else:
            execute_query(
                'INSERT INTO users (username, password) VALUES (?, ?)', 
                (username, hashed_password.decode('utf-8'))
            )
        
        return jsonify({'message': '注册成功'}), 201
        
    except Exception as e:
        print(f"注册错误: {e}")
        return jsonify({'message': '注册失败，请重试'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username') if data.get('username') is not None else ''
    password = data.get('password') if data.get('password') is not None else ''
    
    username = username.strip() if isinstance(username, str) else ''
    password = password.strip() if isinstance(password, str) else ''
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    try:
        # 查找用户
        if IS_PRODUCTION:
            user = execute_query(
                'SELECT * FROM users WHERE username = %s', 
                (username,), 
                fetch_one=True
            )
        else:
            user = execute_query(
                'SELECT * FROM users WHERE username = ?', 
                (username,), 
                fetch_one=True
            )
        
        if not user:
            return jsonify({'message': '用户名或密码错误'}), 401
        
        # 验证密码
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # 创建JWT token
            token = create_access_token(
                identity={'user_id': user['id'], 'username': user['username']}
            )
            return jsonify({'token': token, 'username': user['username'], 'message': '登录成功'}), 200
        else:
            return jsonify({'message': '用户名或密码错误'}), 401
            
    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({'message': '登录失败，请重试'}), 500

# 名言相关路由
@app.route('/api/quotes', methods=['GET'])
def get_quotes():
    page = max(int(request.args.get('page', 1)), 1)  # 确保页码至少为1
    page_size = max(min(int(request.args.get('pageSize', 10)), 50), 1)  # 限制页面大小在1-50之间
    offset = (page - 1) * page_size
    
    try:
        # 获取总数
        if IS_PRODUCTION:
            total_result = execute_query('SELECT COUNT(*) as count FROM quotes', fetch_one=True)
            total = total_result['count']
            
            # 获取分页数据
            quotes = execute_query('''
                SELECT q.*, u.username as added_by 
                FROM quotes q 
                LEFT JOIN users u ON q.user_id = u.id 
                ORDER BY q.created_at DESC 
                LIMIT %s OFFSET %s
            ''', (page_size, offset), fetch_all=True)
        else:
            total_result = execute_query('SELECT COUNT(*) as count FROM quotes', fetch_one=True)
            total = total_result['count']
            
            # 获取分页数据
            quotes = execute_query('''
                SELECT q.*, u.username as added_by 
                FROM quotes q 
                LEFT JOIN users u ON q.user_id = u.id 
                ORDER BY q.created_at DESC 
                LIMIT ? OFFSET ?
            ''', (page_size, offset), fetch_all=True)
        
        # 转换为字典列表
        quotes_list = [dict(quote) for quote in quotes]
        
        return jsonify({
            'quotes': quotes_list,
            'total': total,
            'page': page,
            'page_size': page_size,
            'pageSize': page_size,  # 兼容旧的字段名
            'total_pages': (total + page_size - 1) // page_size
        }), 200
        
    except Exception as e:
        print(f"获取名言错误: {e}")
        return jsonify({'message': '获取名言失败'}), 500

@app.route('/api/quotes', methods=['POST'])
@jwt_required()
def add_quote():
    current_user = get_jwt_identity()
    data = request.get_json()
    content = data.get('content') if data.get('content') is not None else ''
    author = data.get('author') if data.get('author') is not None else ''
    
    content = content.strip() if isinstance(content, str) else ''
    author = author.strip() if isinstance(author, str) else ''
    
    if not content or not author:
        return jsonify({'message': '内容和作者不能为空'}), 400
    
    try:
        if IS_PRODUCTION:
            execute_query(
                'INSERT INTO quotes (content, author, user_id) VALUES (%s, %s, %s)',
                (content, author, current_user['user_id'])
            )
        else:
            execute_query(
                'INSERT INTO quotes (content, author, user_id) VALUES (?, ?, ?)', 
                (content, author, current_user['user_id'])
            )
        
        return jsonify({'message': '添加成功'}), 201
        
    except Exception as e:
        print(f"添加名言错误: {e}")
        return jsonify({'message': '添加失败，请重试'}), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'API 端点不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': '服务器内部错误'}), 500

if __name__ == '__main__':
    # 初始化数据库
    try:
        init_database()
    except Exception as e:
        print(f"❌ 数据库初始化错误: {e}")
        exit(1)
    
    # 服务器配置
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    print(f"🚀 启动服务器: http://0.0.0.0:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

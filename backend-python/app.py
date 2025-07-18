from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import sqlite3
import bcrypt
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
jwt = JWTManager(app)

# 启用CORS
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
CORS(app, origins=cors_origins)

# 数据库配置
DATABASE_PATH = os.getenv('DATABASE_PATH', './db/quote.db')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """初始化数据库"""
    try:
        # 确保数据库目录存在
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"Created database directory: {db_dir}")
        
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
        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise

# 初始化数据库
try:
    init_database()
except Exception as e:
    print(f"数据库初始化错误: {e}")

@app.route('/')
def index():
    return {'message': 'Quote API is running (Python Flask)!'}

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

# 用户认证路由
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    # 检查用户名是否只包含空格
    if username.strip() == '':
        return jsonify({'message': '用户名不能为空或仅包含空格'}), 400
    
    # 检查密码是否只包含空格
    if password.strip() == '':
        return jsonify({'message': '密码不能为空或仅包含空格'}), 400
    
    # 检查用户是否已存在
    conn = get_db_connection()
    existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    if existing_user:
        conn.close()
        return jsonify({'message': '用户已存在'}), 400
    
    # 加密密码
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # 插入新用户
    try:
        conn.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, hashed_password)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': '注册成功'}), 201
    except Exception as e:
        conn.close()
        return jsonify({'message': '注册失败'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    # 查找用户
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'message': '用户不存在'}), 401
    
    # 验证密码
    if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'message': '密码错误'}), 401
    
    # 创建JWT token
    access_token = create_access_token(identity=str(user['id']))
    
    return jsonify({
        'message': '登录成功',
        'token': access_token,
        'user': {'id': user['id'], 'username': user['username']}
    }), 200

# 名言相关路由
@app.route('/api/quotes', methods=['GET'])
def get_quotes():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        
        # 验证分页参数
        if page < 1:
            page = 1
        if page_size <= 0:
            page_size = 10
        
        offset = (page - 1) * page_size
        
        conn = get_db_connection()
        
        # 获取总数
        total_count = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
        
        # 获取分页数据
        quotes = conn.execute('''
            SELECT quotes.id, quotes.content, quotes.author, quotes.created_at, 
                   users.username AS added_by
            FROM quotes
            LEFT JOIN users ON quotes.user_id = users.id
            ORDER BY quotes.created_at DESC
            LIMIT ? OFFSET ?
        ''', (page_size, offset)).fetchall()
        
        conn.close()
        
        # 转换为字典格式
        quotes_list = []
        for quote in quotes:
            quotes_list.append({
                'id': quote['id'],
                'content': quote['content'],
                'author': quote['author'],
                'added_by': quote['added_by'],
                'created_at': quote['created_at']
            })
        
        return jsonify({
            'quotes': quotes_list,
            'total': total_count,
            'page': page,
            'pageSize': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
    except Exception as e:
        print(f"获取名言出错: {e}")
        return jsonify({'error': '获取名言失败'}), 500
        quotes_list.append({
            'id': quote['id'],
            'content': quote['content'],
            'author': quote['author'],
            'created_at': quote['created_at'],
            'added_by': quote['added_by']
        })
    
    return jsonify({
        'total': total_count,
        'page': page,
        'pageSize': page_size,
        'quotes': quotes_list
    }), 200

@app.route('/api/quotes', methods=['POST'])
@jwt_required()
def add_quote():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    content = data.get('content')
    author = data.get('author')
    
    if not content or not author:
        return jsonify({'message': '内容和作者不能为空'}), 400
    
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            'INSERT INTO quotes (content, author, user_id) VALUES (?, ?, ?)',
            (content, author, current_user_id)
        )
        quote_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': quote_id,
            'content': content,
            'author': author,
            'user_id': current_user_id,
            'message': '添加成功'
        }), 201
    except Exception as e:
        conn.close()
        return jsonify({'message': '添加失败'}), 500

if __name__ == '__main__':
    # 初始化数据库
    try:
        init_database()
    except Exception as e:
        print(f"数据库初始化错误: {e}")
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)

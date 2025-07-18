import os
import tempfile
import pytest
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, get_db_connection
from database import init_database, seed_quotes

@pytest.fixture
def client():
    """创建测试客户端"""
    # 创建临时数据库
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    # 设置测试数据库路径
    global db_path
    db_path = app.config['DATABASE']
    
    with app.test_client() as client:
        with app.app_context():
            # 初始化测试数据库
            init_test_db()
        yield client
    
    # 清理临时数据库
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def init_test_db():
    """初始化测试数据库"""
    import sqlite3
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建名言表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            user_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # 插入测试数据
    test_quotes = [
        ("测试名言1", "测试作者1"),
        ("测试名言2", "测试作者2"),
        ("测试名言3", "测试作者3")
    ]
    
    for content, author in test_quotes:
        cursor.execute(
            'INSERT INTO quotes (content, author) VALUES (?, ?)',
            (content, author)
        )
    
    conn.commit()
    conn.close()

# 修改 app.py 中的 get_db_connection 函数来支持测试
def get_test_db_connection():
    """获取测试数据库连接"""
    import sqlite3
    if hasattr(app, 'config') and 'DATABASE' in app.config:
        conn = sqlite3.connect(app.config['DATABASE'])
    else:
        conn = sqlite3.connect('./db/quote.db')
    conn.row_factory = sqlite3.Row
    return conn

# 在测试期间替换数据库连接函数
import app as app_module
app_module.get_db_connection = get_test_db_connection

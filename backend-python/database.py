import sqlite3
import os
from datetime import datetime

# 创建数据库目录
db_dir = './db'
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# 数据库文件路径
db_path = os.path.join(db_dir, 'quote.db')

def init_database():
    """初始化数据库表"""
    conn = sqlite3.connect(db_path)
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
    
    conn.commit()
    conn.close()
    print('数据库初始化完成')

def seed_quotes():
    """插入默认名言数据"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查是否已经有数据
    cursor.execute('SELECT COUNT(*) FROM quotes')
    count = cursor.fetchone()[0]
    
    if count == 0:
        quotes = [
            ("天生我材必有用。", "李白"),
            ("路漫漫其修远兮，吾将上下而求索。", "屈原"),
            ("不积跬步，无以至千里。", "荀子"),
            ("千里之行，始于足下。", "老子"),
            ("会当凌绝顶，一览众山小。", "杜甫"),
            ("海内存知己，天涯若比邻。", "王勃"),
            ("长风破浪会有时，直挂云帆济沧海。", "李白"),
            ("人生自古谁无死，留取丹心照汗青。", "文天祥"),
            ("少壮不努力，老大徒伤悲。", "《汉乐府》"),
            ("业精于勤荒于嬉，行成于思毁于随。", "韩愈"),
            ("黑发不知勤学早，白首方悔读书迟。", "颜真卿"),
            ("三人行，必有我师焉。", "孔子"),
            ("己所不欲，勿施于人。", "孔子"),
            ("知之者不如好之者，好之者不如乐之者。", "孔子"),
            ("敏而好学，不耻下问。", "孔子"),
            ("学而不思则罔，思而不学则殆。", "孔子"),
            ("读万卷书，行万里路。", "刘彝"),
            ("书山有路勤为径，学海无涯苦作舟。", "韩愈"),
            ("千教万教教人求真，千学万学学做真人。", "陶行知"),
            ("立身以立学为先，立学以读书为本。", "欧阳修")
        ]
        
        for content, author in quotes:
            cursor.execute(
                'INSERT INTO quotes (content, author) VALUES (?, ?)',
                (content, author)
            )
        
        conn.commit()
        print(f'已插入{len(quotes)}条名言')
    else:
        print('数据库已有数据，跳过seed')
    
    conn.close()

if __name__ == '__main__':
    init_database()
    seed_quotes()

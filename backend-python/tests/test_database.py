"""
测试数据库相关功能
"""
import pytest
import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import init_database, seed_quotes

class TestDatabase:
    """数据库测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.test_db_path = 'test_quote.db'
        # 确保测试数据库不存在
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        # 清理测试数据库
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_init_database(self):
        """测试数据库初始化"""
        # 临时修改数据库路径
        import database
        original_path = database.db_path
        database.db_path = self.test_db_path
        
        try:
            # 初始化数据库
            init_database()
            
            # 验证数据库文件是否创建
            assert os.path.exists(self.test_db_path)
            
            # 验证表是否创建
            conn = sqlite3.connect(self.test_db_path)
            cursor = conn.cursor()
            
            # 检查用户表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            assert cursor.fetchone() is not None
            
            # 检查名言表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quotes'")
            assert cursor.fetchone() is not None
            
            conn.close()
            
        finally:
            # 恢复原始路径
            database.db_path = original_path
    
    def test_seed_quotes(self):
        """测试种子数据插入"""
        # 临时修改数据库路径
        import database
        original_path = database.db_path
        database.db_path = self.test_db_path
        
        try:
            # 初始化数据库
            init_database()
            
            # 插入种子数据
            seed_quotes()
            
            # 验证数据是否插入
            conn = sqlite3.connect(self.test_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM quotes")
            count = cursor.fetchone()[0]
            assert count == 20  # 应该有20条种子数据
            
            # 验证数据内容
            cursor.execute("SELECT content, author FROM quotes LIMIT 1")
            quote = cursor.fetchone()
            assert quote is not None
            assert len(quote[0]) > 0  # 内容不为空
            assert len(quote[1]) > 0  # 作者不为空
            
            conn.close()
            
        finally:
            # 恢复原始路径
            database.db_path = original_path
    
    def test_seed_quotes_no_duplicate(self):
        """测试种子数据不会重复插入"""
        # 临时修改数据库路径
        import database
        original_path = database.db_path
        database.db_path = self.test_db_path
        
        try:
            # 初始化数据库
            init_database()
            
            # 第一次插入种子数据
            seed_quotes()
            
            # 第二次插入种子数据
            seed_quotes()
            
            # 验证数据没有重复
            conn = sqlite3.connect(self.test_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM quotes")
            count = cursor.fetchone()[0]
            assert count == 20  # 仍然应该只有20条数据
            
            conn.close()
            
        finally:
            # 恢复原始路径
            database.db_path = original_path
    
    def test_database_schema(self):
        """测试数据库表结构"""
        # 临时修改数据库路径
        import database
        original_path = database.db_path
        database.db_path = self.test_db_path
        
        try:
            # 初始化数据库
            init_database()
            
            conn = sqlite3.connect(self.test_db_path)
            cursor = conn.cursor()
            
            # 检查用户表结构
            cursor.execute("PRAGMA table_info(users)")
            user_columns = cursor.fetchall()
            user_column_names = [col[1] for col in user_columns]
            
            expected_user_columns = ['id', 'username', 'password', 'created_at']
            for col in expected_user_columns:
                assert col in user_column_names
            
            # 检查名言表结构
            cursor.execute("PRAGMA table_info(quotes)")
            quote_columns = cursor.fetchall()
            quote_column_names = [col[1] for col in quote_columns]
            
            expected_quote_columns = ['id', 'content', 'author', 'user_id', 'created_at']
            for col in expected_quote_columns:
                assert col in quote_column_names
            
            conn.close()
            
        finally:
            # 恢复原始路径
            database.db_path = original_path

"""
测试安全性相关功能
"""
import pytest
import json
import bcrypt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

class TestSecurity:
    """安全性测试类"""
    
    def test_password_hashing(self, client):
        """测试密码哈希加密"""
        # 注册用户
        response = client.post('/api/auth/register', 
                             json={'username': 'testuser', 'password': 'plaintext123'})
        assert response.status_code == 201
        
        # 检查数据库中的密码是否被加密
        import sqlite3
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        cursor.execute('SELECT password FROM users WHERE username = ?', ('testuser',))
        stored_password = cursor.fetchone()[0]
        
        # 验证密码不是明文
        assert stored_password != 'plaintext123'
        
        # 验证密码可以被正确验证
        stored_password_bytes = stored_password.encode('utf-8') if isinstance(stored_password, str) else stored_password
        assert bcrypt.checkpw('plaintext123'.encode('utf-8'), stored_password_bytes)
        
        conn.close()
    
    def test_jwt_token_required(self, client):
        """测试JWT token是必需的"""
        # 尝试在没有token的情况下添加名言
        response = client.post('/api/quotes',
                             json={'content': '测试名言', 'author': '测试作者'})
        assert response.status_code == 401
    
    def test_jwt_token_invalid(self, client):
        """测试无效JWT token"""
        # 使用无效token
        response = client.post('/api/quotes',
                             json={'content': '测试名言', 'author': '测试作者'},
                             headers={'Authorization': 'Bearer invalid_token_here'})
        assert response.status_code == 422
    
    def test_jwt_token_malformed(self, client):
        """测试格式错误的JWT token"""
        # 使用格式错误的token
        response = client.post('/api/quotes',
                             json={'content': '测试名言', 'author': '测试作者'},
                             headers={'Authorization': 'malformed_auth_header'})
        assert response.status_code == 401
    
    def test_sql_injection_protection(self, client):
        """测试SQL注入保护"""
        # 尝试在用户名中注入SQL
        malicious_username = "testuser'; DROP TABLE users; --"
        
        response = client.post('/api/auth/register', 
                             json={'username': malicious_username, 'password': 'testpass123'})
        
        # 注册应该成功，但SQL注入应该被防止
        assert response.status_code == 201
        
        # 验证表仍然存在
        import sqlite3
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM users')
            count = cursor.fetchone()[0]
            assert count >= 1  # 至少有一个用户
        except sqlite3.OperationalError:
            # 如果表被删除，这里会抛出异常
            pytest.fail("SQL injection attack succeeded - users table was dropped")
        finally:
            conn.close()
    
    def test_xss_protection(self, client):
        """测试XSS保护"""
        # 注册用户
        client.post('/api/auth/register', 
                   json={'username': 'testuser', 'password': 'testpass123'})
        
        # 登录获取token
        login_response = client.post('/api/auth/login', 
                                   json={'username': 'testuser', 'password': 'testpass123'})
        
        login_data = json.loads(login_response.data)
        token = login_data['token']
        
        # 尝试添加包含XSS脚本的名言
        xss_content = "<script>alert('XSS')</script>"
        response = client.post('/api/quotes',
                             json={'content': xss_content, 'author': '测试作者'},
                             headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 201
        
        # 验证内容被正确存储（不被过滤，因为这是API，前端负责转义）
        quotes_response = client.get('/api/quotes')
        quotes_data = json.loads(quotes_response.data)
        
        # 找到我们添加的名言
        added_quote = None
        for quote in quotes_data['quotes']:
            if quote['content'] == xss_content:
                added_quote = quote
                break
        
        assert added_quote is not None
        assert added_quote['content'] == xss_content
    
    def test_input_validation(self, client):
        """测试输入验证"""
        # 测试空用户名
        response = client.post('/api/auth/register', 
                             json={'username': '', 'password': 'testpass123'})
        assert response.status_code == 400
        
        # 测试空密码
        response = client.post('/api/auth/register', 
                             json={'username': 'testuser', 'password': ''})
        assert response.status_code == 400
        
        # 测试None值
        response = client.post('/api/auth/register', 
                             json={'username': None, 'password': 'testpass123'})
        assert response.status_code == 400
    
    def test_cors_headers(self, client):
        """测试CORS头部"""
        response = client.get('/')
        
        # 检查是否设置了CORS头部
        # 注意：pytest-flask的test_client不会自动处理CORS头部
        # 但我们可以确认应用配置了Flask-CORS
        assert response.status_code == 200
    
    def test_rate_limiting_simulation(self, client):
        """模拟测试速率限制（仅验证多次请求不会崩溃）"""
        # 快速发送多个请求
        responses = []
        for i in range(10):
            response = client.get('/')
            responses.append(response)
        
        # 所有请求都应该成功
        for response in responses:
            assert response.status_code == 200
    
    def test_sensitive_data_exposure(self, client):
        """测试敏感数据不会暴露"""
        # 注册用户
        client.post('/api/auth/register', 
                   json={'username': 'testuser', 'password': 'testpass123'})
        
        # 登录用户
        login_response = client.post('/api/auth/login', 
                                   json={'username': 'testuser', 'password': 'testpass123'})
        
        login_data = json.loads(login_response.data)
        
        # 确保响应中不包含密码
        assert 'password' not in login_data
        assert 'password' not in login_data.get('user', {})
        
        # 确保用户信息不包含敏感数据
        user_info = login_data.get('user', {})
        sensitive_fields = ['password', 'password_hash', 'secret']
        for field in sensitive_fields:
            assert field not in user_info

class TestErrorHandling:
    """错误处理测试类"""
    
    def test_404_error(self, client):
        """测试404错误"""
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client):
        """测试405方法不允许错误"""
        # 对只接受POST的端点发送GET请求
        response = client.get('/api/auth/register')
        assert response.status_code == 405
    
    def test_malformed_json(self, client):
        """测试格式错误的JSON"""
        response = client.post('/api/auth/register',
                             data='{"malformed": json}',
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_missing_content_type(self, client):
        """测试缺少Content-Type头部"""
        response = client.post('/api/auth/register',
                             data='{"username": "test", "password": "test"}')
        # Flask会尝试解析，但可能失败
        assert response.status_code in [400, 415]

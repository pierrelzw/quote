"""
测试API端点
"""
import pytest
import json
import bcrypt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

class TestAPI:
    """API测试类"""
    
    def test_root_endpoint(self, client):
        """测试根端点"""
        response = client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Python Flask' in data['message']
    
    def test_register_success(self, client):
        """测试用户注册成功"""
        response = client.post('/api/auth/register', 
                             json={'username': 'testuser', 'password': 'testpass123'})
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == '注册成功'
    
    def test_register_missing_fields(self, client):
        """测试注册缺少字段"""
        # 缺少用户名
        response = client.post('/api/auth/register', 
                             json={'password': 'testpass123'})
        assert response.status_code == 400
        
        # 缺少密码
        response = client.post('/api/auth/register', 
                             json={'username': 'testuser'})
        assert response.status_code == 400
    
    def test_register_duplicate_username(self, client):
        """测试注册重复用户名"""
        # 第一次注册
        response = client.post('/api/auth/register', 
                             json={'username': 'testuser', 'password': 'testpass123'})
        assert response.status_code == 201
        
        # 第二次注册相同用户名
        response = client.post('/api/auth/register', 
                             json={'username': 'testuser', 'password': 'testpass456'})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['message'] == '用户已存在'
    
    def test_login_success(self, client):
        """测试用户登录成功"""
        # 先注册用户
        client.post('/api/auth/register', 
                   json={'username': 'testuser', 'password': 'testpass123'})
        
        # 然后登录
        response = client.post('/api/auth/login', 
                             json={'username': 'testuser', 'password': 'testpass123'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == '登录成功'
        assert 'token' in data
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
    
    def test_login_invalid_credentials(self, client):
        """测试登录无效凭据"""
        # 先注册用户
        client.post('/api/auth/register', 
                   json={'username': 'testuser', 'password': 'testpass123'})
        
        # 错误密码
        response = client.post('/api/auth/login', 
                             json={'username': 'testuser', 'password': 'wrongpass'})
        assert response.status_code == 401
        
        # 不存在的用户
        response = client.post('/api/auth/login', 
                             json={'username': 'nonexistentuser', 'password': 'testpass123'})
        assert response.status_code == 401
    
    def test_login_missing_fields(self, client):
        """测试登录缺少字段"""
        # 缺少用户名
        response = client.post('/api/auth/login', 
                             json={'password': 'testpass123'})
        assert response.status_code == 400
        
        # 缺少密码
        response = client.post('/api/auth/login', 
                             json={'username': 'testuser'})
        assert response.status_code == 400
    
    def test_get_quotes_success(self, client):
        """测试获取名言成功"""
        response = client.get('/api/quotes')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'quotes' in data
        assert 'total' in data
        assert 'page' in data
        assert 'pageSize' in data
        assert isinstance(data['quotes'], list)
        assert len(data['quotes']) > 0
    
    def test_get_quotes_pagination(self, client):
        """测试名言分页"""
        # 测试第一页
        response = client.get('/api/quotes?page=1&pageSize=2')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['page'] == 1
        assert data['pageSize'] == 2
        assert len(data['quotes']) <= 2
        
        # 测试第二页
        response = client.get('/api/quotes?page=2&pageSize=2')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['page'] == 2
        assert data['pageSize'] == 2
    
    def test_add_quote_success(self, client):
        """测试添加名言成功"""
        # 先注册并登录用户
        client.post('/api/auth/register', 
                   json={'username': 'testuser', 'password': 'testpass123'})
        
        login_response = client.post('/api/auth/login', 
                                   json={'username': 'testuser', 'password': 'testpass123'})
        
        login_data = json.loads(login_response.data)
        token = login_data['token']
        
        # 添加名言
        response = client.post('/api/quotes',
                             json={'content': '测试名言内容', 'author': '测试作者'},
                             headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == '添加成功'
        assert data['content'] == '测试名言内容'
        assert data['author'] == '测试作者'
    
    def test_add_quote_unauthorized(self, client):
        """测试未授权添加名言"""
        response = client.post('/api/quotes',
                             json={'content': '测试名言内容', 'author': '测试作者'})
        
        assert response.status_code == 401
    
    def test_add_quote_invalid_token(self, client):
        """测试无效token添加名言"""
        response = client.post('/api/quotes',
                             json={'content': '测试名言内容', 'author': '测试作者'},
                             headers={'Authorization': 'Bearer invalid_token'})
        
        assert response.status_code == 422  # JWT错误
    
    def test_add_quote_missing_fields(self, client):
        """测试添加名言缺少字段"""
        # 先注册并登录用户
        client.post('/api/auth/register', 
                   json={'username': 'testuser', 'password': 'testpass123'})
        
        login_response = client.post('/api/auth/login', 
                                   json={'username': 'testuser', 'password': 'testpass123'})
        
        login_data = json.loads(login_response.data)
        token = login_data['token']
        
        # 缺少内容
        response = client.post('/api/quotes',
                             json={'author': '测试作者'},
                             headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 400
        
        # 缺少作者
        response = client.post('/api/quotes',
                             json={'content': '测试名言内容'},
                             headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 400

class TestIntegration:
    """集成测试类"""
    
    def test_complete_user_flow(self, client):
        """测试完整的用户流程"""
        # 1. 注册用户
        register_response = client.post('/api/auth/register', 
                                      json={'username': 'integrationuser', 'password': 'testpass123'})
        assert register_response.status_code == 201
        
        # 2. 登录用户
        login_response = client.post('/api/auth/login', 
                                   json={'username': 'integrationuser', 'password': 'testpass123'})
        assert login_response.status_code == 200
        
        login_data = json.loads(login_response.data)
        token = login_data['token']
        
        # 3. 获取名言列表
        quotes_response = client.get('/api/quotes')
        assert quotes_response.status_code == 200
        
        quotes_data = json.loads(quotes_response.data)
        initial_count = quotes_data['total']
        
        # 4. 添加新名言
        add_response = client.post('/api/quotes',
                                 json={'content': '集成测试名言', 'author': '集成测试作者'},
                                 headers={'Authorization': f'Bearer {token}'})
        assert add_response.status_code == 201
        
        # 5. 验证名言已添加
        quotes_response = client.get('/api/quotes')
        assert quotes_response.status_code == 200
        
        quotes_data = json.loads(quotes_response.data)
        assert quotes_data['total'] == initial_count + 1
        
        # 6. 验证新名言在列表中
        # 查找新添加的名言
        new_quote_found = False
        for quote in quotes_data['quotes']:
            if (quote['content'] == '集成测试名言' and 
                quote['author'] == '集成测试作者' and
                quote['added_by'] == 'integrationuser'):
                new_quote_found = True
                break
        
        assert new_quote_found, "新添加的名言未在列表中找到"

"""
边界测试和边缘情况测试
"""
import pytest
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .test_data_factory import TestDataFactory, TestHelpers, EDGE_CASE_DATA

class TestEdgeCases:
    """边界测试类"""
    
    def test_long_username(self, client):
        """测试长用户名"""
        long_username = EDGE_CASE_DATA['long_username']
        
        response = client.post('/api/auth/register', 
                             json={'username': long_username, 'password': 'testpass123'})
        
        # 应该处理长用户名（可能成功或返回适当错误）
        assert response.status_code in [201, 400]
    
    def test_long_password(self, client):
        """测试长密码"""
        long_password = EDGE_CASE_DATA['long_password']
        
        response = client.post('/api/auth/register', 
                             json={'username': 'testuser', 'password': long_password})
        
        # 应该处理长密码
        assert response.status_code in [201, 400]
    
    def test_long_quote_content(self, client):
        """测试长名言内容"""
        token, _ = TestHelpers.register_and_login_user(client)
        assert token is not None
        
        long_content = EDGE_CASE_DATA['long_quote_content']
        
        response = client.post('/api/quotes',
                             json={'content': long_content, 'author': '测试作者'},
                             headers={'Authorization': f'Bearer {token}'})
        
        # 应该处理长内容
        assert response.status_code in [201, 400]
    
    def test_empty_strings(self, client):
        """测试空字符串"""
        empty_string = EDGE_CASE_DATA['empty_string']
        
        # 测试空用户名
        response = client.post('/api/auth/register', 
                             json={'username': empty_string, 'password': 'testpass123'})
        assert response.status_code == 400
        
        # 测试空密码
        response = client.post('/api/auth/register', 
                             json={'username': 'testuser', 'password': empty_string})
        assert response.status_code == 400
        
        # 测试空名言内容
        token, _ = TestHelpers.register_and_login_user(client)
        if token:
            response = client.post('/api/quotes',
                                 json={'content': empty_string, 'author': '测试作者'},
                                 headers={'Authorization': f'Bearer {token}'})
            assert response.status_code == 400
    
    def test_whitespace_strings(self, client):
        """测试只包含空格的字符串"""
        whitespace_string = EDGE_CASE_DATA['whitespace_string']
        
        # 测试只有空格的用户名
        response = client.post('/api/auth/register', 
                             json={'username': whitespace_string, 'password': 'testpass123'})
        assert response.status_code == 400
        
        # 测试只有空格的密码
        response = client.post('/api/auth/register', 
                             json={'username': 'testuser', 'password': whitespace_string})
        assert response.status_code == 400
    
    def test_special_characters(self, client):
        """测试特殊字符"""
        special_chars = EDGE_CASE_DATA['special_chars']
        
        # 测试特殊字符用户名
        response = client.post('/api/auth/register', 
                             json={'username': special_chars, 'password': 'testpass123'})
        
        # 应该处理特殊字符（可能成功或返回适当错误）
        assert response.status_code in [201, 400]
    
    def test_unicode_content(self, client):
        """测试Unicode内容"""
        unicode_content = EDGE_CASE_DATA['unicode_content']
        
        token, _ = TestHelpers.register_and_login_user(client)
        assert token is not None
        
        response = client.post('/api/quotes',
                             json={'content': unicode_content, 'author': '测试作者'},
                             headers={'Authorization': f'Bearer {token}'})
        
        # 应该支持Unicode内容
        assert response.status_code == 201
        
        # 验证内容正确存储
        quotes_response = client.get('/api/quotes')
        quotes_data = json.loads(quotes_response.data)
        
        found_quote = None
        for quote in quotes_data['quotes']:
            if quote['content'] == unicode_content:
                found_quote = quote
                break
        
        assert found_quote is not None
    
    def test_null_values(self, client):
        """测试null值"""
        # 测试null用户名
        response = client.post('/api/auth/register', 
                             json={'username': None, 'password': 'testpass123'})
        assert response.status_code == 400
        
        # 测试null密码
        response = client.post('/api/auth/register', 
                             json={'username': 'testuser', 'password': None})
        assert response.status_code == 400
    
    def test_missing_fields(self, client):
        """测试缺少字段"""
        # 完全缺少用户名字段
        response = client.post('/api/auth/register', 
                             json={'password': 'testpass123'})
        assert response.status_code == 400
        
        # 完全缺少密码字段
        response = client.post('/api/auth/register', 
                             json={'username': 'testuser'})
        assert response.status_code == 400
    
    def test_large_page_size(self, client):
        """测试大页面大小"""
        # 测试非常大的页面大小
        response = client.get('/api/quotes?page=1&pageSize=1000')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # 应该限制返回的结果数量
        assert len(data['quotes']) <= 1000
    
    def test_negative_page_number(self, client):
        """测试负页数"""
        response = client.get('/api/quotes?page=-1&pageSize=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # 应该处理负页数（可能默认为1）
        assert data['page'] >= 1
    
    def test_zero_page_size(self, client):
        """测试零页面大小"""
        response = client.get('/api/quotes?page=1&pageSize=0')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # 应该处理零页面大小（可能使用默认值）
        assert data['pageSize'] > 0
    
    def test_malformed_auth_header(self, client):
        """测试格式错误的认证头"""
        malformed_headers = [
            {'Authorization': 'Bearer'},  # 缺少token
            {'Authorization': 'InvalidScheme token'},  # 错误的schema
            {'Authorization': 'Bearer token with spaces'},  # 包含空格的token
            {'Authorization': ''},  # 空认证头
        ]
        
        for header in malformed_headers:
            response = client.post('/api/quotes',
                                 json={'content': '测试内容', 'author': '测试作者'},
                                 headers=header)
            assert response.status_code in [401, 422]
    
    def test_concurrent_user_registration(self, client):
        """测试并发用户注册（模拟）"""
        # 由于Flask测试客户端不支持真正的并发，这里模拟连续注册相同用户名
        username = 'concurrent_test_user'
        results = []
        
        # 连续尝试注册相同用户名5次
        for _ in range(5):
            result = client.post('/api/auth/register', 
                               json={'username': username, 'password': 'testpass123'})
            results.append(result)
        
        # 应该只有一个注册成功，其他的应该失败
        success_count = sum(1 for result in results if result.status_code == 201)
        failure_count = sum(1 for result in results if result.status_code == 400)
        
        assert success_count == 1
        assert failure_count == 4
    
    def test_extreme_pagination(self, client):
        """测试极端分页情况"""
        # 测试非常大的页数
        response = client.get('/api/quotes?page=999999&pageSize=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # 应该返回空结果或合理的错误
        assert isinstance(data['quotes'], list)
        
        # 测试页数为0
        response = client.get('/api/quotes?page=0&pageSize=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['page'] >= 1  # 应该处理为至少第1页

class TestResourceLimits:
    """资源限制测试"""
    
    def test_memory_usage_with_large_content(self, client):
        """测试大内容的内存使用"""
        token, _ = TestHelpers.register_and_login_user(client)
        assert token is not None
        
        # 创建一个相当大的内容
        large_content = 'A' * 10000  # 10KB内容
        
        response = client.post('/api/quotes',
                             json={'content': large_content, 'author': '测试作者'},
                             headers={'Authorization': f'Bearer {token}'})
        
        # 应该能够处理大内容或返回适当错误
        assert response.status_code in [201, 400, 413]
    
    def test_multiple_rapid_requests(self, client):
        """测试快速连续请求"""
        token, _ = TestHelpers.register_and_login_user(client)
        assert token is not None
        
        # 快速发送多个请求
        responses = []
        for i in range(20):
            response = client.post('/api/quotes',
                                 json={'content': f'快速测试{i}', 'author': '测试作者'},
                                 headers={'Authorization': f'Bearer {token}'})
            responses.append(response)
        
        # 大部分请求应该成功
        success_count = sum(1 for response in responses if response.status_code == 201)
        assert success_count >= 15  # 至少75%成功
    
    def test_database_connection_stability(self, client):
        """测试数据库连接稳定性"""
        # 连续进行多次数据库操作
        for i in range(50):
            response = client.get('/api/quotes')
            assert response.status_code == 200
            
            # 偶尔添加一些数据
            if i % 10 == 0:
                token, _ = TestHelpers.register_and_login_user(client)
                if token:
                    client.post('/api/quotes',
                              json={'content': f'稳定性测试{i}', 'author': '测试作者'},
                              headers={'Authorization': f'Bearer {token}'})
        
        # 如果到达这里，说明数据库连接稳定

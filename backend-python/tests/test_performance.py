"""
性能和负载测试
"""
import pytest
import json
import time

class TestPerformance:
    """性能测试类"""
    
    def test_response_time_root_endpoint(self, client):
        """测试根端点响应时间"""
        start_time = time.time()
        response = client.get('/')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # 响应时间应该小于1秒
    
    def test_response_time_quotes_endpoint(self, client):
        """测试名言端点响应时间"""
        start_time = time.time()
        response = client.get('/api/quotes')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # 响应时间应该小于2秒
    
    def test_multiple_concurrent_requests(self, client):
        """测试并发请求（模拟）"""
        # 由于Flask测试客户端不支持真正的并发，这里模拟连续请求
        responses = []
        start_time = time.time()

        # 连续发送10个请求
        for _ in range(10):
            response = client.get('/')
            responses.append(response)
            assert response.status_code == 200

        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证所有响应都成功
        assert len(responses) == 10
        assert all(r.status_code == 200 for r in responses)
        
        # 验证响应时间合理（每个请求平均不超过100ms）
        avg_time = total_time / 10
        assert avg_time < 0.1, f"平均响应时间过长: {avg_time:.3f}s"
    
    def test_pagination_performance(self, client):
        """测试分页性能"""
        # 测试不同页面大小的响应时间
        page_sizes = [5, 10, 20, 50]
        
        for page_size in page_sizes:
            start_time = time.time()
            response = client.get(f'/api/quotes?page=1&pageSize={page_size}')
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 1.0  # 每个查询应该在1秒内完成
            
            data = json.loads(response.data)
            assert len(data['quotes']) <= page_size
    
    def test_memory_usage_stability(self, client):
        """测试内存使用稳定性（简单版本）"""
        # 连续发送多个请求，检查是否有内存泄漏迹象
        responses = []
        
        for i in range(50):
            response = client.get('/api/quotes')
            responses.append(response)
        
        # 所有请求都应该成功
        for response in responses:
            assert response.status_code == 200
        
        # 如果有严重的内存泄漏，这个测试可能会失败或变慢
        # 这是一个基本的稳定性检查
    
    def test_database_query_performance(self, client):
        """测试数据库查询性能"""
        # 注册用户
        client.post('/api/auth/register', 
                   json={'username': 'perfuser', 'password': 'testpass123'})
        
        # 登录获取token
        login_response = client.post('/api/auth/login', 
                                   json={'username': 'perfuser', 'password': 'testpass123'})
        
        login_data = json.loads(login_response.data)
        token = login_data['token']
        
        # 测试添加多个名言的性能
        add_times = []
        
        for i in range(10):
            start_time = time.time()
            response = client.post('/api/quotes',
                                 json={'content': f'性能测试名言{i}', 'author': '性能测试作者'},
                                 headers={'Authorization': f'Bearer {token}'})
            end_time = time.time()
            
            add_times.append(end_time - start_time)
            assert response.status_code == 201
        
        # 平均添加时间应该合理
        avg_add_time = sum(add_times) / len(add_times)
        assert avg_add_time < 0.5  # 平均每次添加应该在0.5秒内完成
        
        # 测试查询性能
        start_time = time.time()
        response = client.get('/api/quotes?page=1&pageSize=20')
        end_time = time.time()
        
        query_time = end_time - start_time
        assert response.status_code == 200
        assert query_time < 1.0  # 查询应该在1秒内完成

class TestLoadSimulation:
    """负载模拟测试类"""
    
    def test_user_registration_load(self, client):
        """测试用户注册负载（模拟）"""
        # 由于Flask测试客户端不支持真正的并发，这里模拟连续注册
        success_count = 0
        start_time = time.time()
        
        for i in range(20):
            response = client.post('/api/auth/register', 
                                 json={'username': f'loaduser{i}', 'password': 'testpass123'})
            if response.status_code == 201:
                success_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 大部分注册应该成功
        assert success_count >= 15  # 至少75%的注册成功
        assert total_time < 10.0  # 20个注册应该在10秒内完成
    
    def test_mixed_load_scenario(self, client):
        """测试混合负载场景"""
        # 预先注册一些用户
        users = []
        for i in range(5):
            client.post('/api/auth/register', 
                       json={'username': f'mixeduser{i}', 'password': 'testpass123'})
            
            login_response = client.post('/api/auth/login', 
                                       json={'username': f'mixeduser{i}', 'password': 'testpass123'})
            login_data = json.loads(login_response.data)
            users.append(login_data['token'])
        
        def mixed_operations():
            operations = []
            
            # 查询名言
            for _ in range(10):
                response = client.get('/api/quotes')
                operations.append(('GET', response.status_code))
            
            # 添加名言
            for i, token in enumerate(users):
                response = client.post('/api/quotes',
                                     json={'content': f'负载测试名言{i}', 'author': '负载测试'},
                                     headers={'Authorization': f'Bearer {token}'})
                operations.append(('POST', response.status_code))
            
            return operations
        
        # 执行混合操作
        start_time = time.time()
        operations = mixed_operations()
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # 检查操作结果
        get_success = sum(1 for op, status in operations if op == 'GET' and status == 200)
        post_success = sum(1 for op, status in operations if op == 'POST' and status == 201)
        
        assert get_success >= 8  # 至少80%的GET请求成功
        assert post_success >= 3  # 至少60%的POST请求成功
        assert total_time < 10.0  # 总时间应该在10秒内
    
    def test_stress_quotes_endpoint(self, client):
        """压力测试名言端点（模拟）"""
        # 由于Flask测试客户端不支持真正的并发，这里模拟连续请求
        responses = []
        start_time = time.time()

        # 连续发送100个请求
        for _ in range(100):
            response = client.get('/api/quotes')
            responses.append(response)

        end_time = time.time()
        total_time = end_time - start_time
        
        # 统计成功率
        success_count = sum(1 for response in responses if response.status_code == 200)
        success_rate = success_count / len(responses)
        
        assert success_rate >= 0.9  # 至少90%的请求成功
        assert total_time < 30.0  # 100个请求应该在30秒内完成
        
        # 检查响应时间分布
        # 如果所有请求都很快完成，说明系统处理能力良好
        requests_per_second = len(responses) / total_time
        assert requests_per_second >= 5  # 至少每秒处理5个请求

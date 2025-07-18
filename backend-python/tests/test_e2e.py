"""
端到端测试 (E2E Tests)
测试完整的用户流程和系统集成
"""
import pytest
import json
import time
import threading
from app import app


class TestEndToEndWorkflows:
    """端到端工作流测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_complete_user_journey(self, client):
        """测试完整的用户旅程"""
        # 1. 检查系统状态
        health_response = client.get('/health')
        assert health_response.status_code == 200
        
        # 2. 用户注册
        import time
        unique_suffix = str(int(time.time()))
        register_data = {
            'username': f'e2e_user_{unique_suffix}',
            'password': 'secure_password_123'
        }
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(register_data),
                                      content_type='application/json')
        assert register_response.status_code == 201
        register_result = json.loads(register_response.data)
        assert 'token' in register_result
        
        token = register_result['token']
        
        # 3. 用户登录验证
        login_data = {
            'username': f'e2e_user_{unique_suffix}',
            'password': 'secure_password_123'
        }
        login_response = client.post('/api/auth/login',
                                   data=json.dumps(login_data),
                                   content_type='application/json')
        assert login_response.status_code == 200
        login_result = json.loads(login_response.data)
        assert 'token' in login_result
        
        # 验证两个token都是有效的（虽然可能不同）
        login_token = login_result['token']
        assert len(token) > 0
        assert len(login_token) > 0
        
        # 4. 获取初始名言列表
        quotes_response = client.get('/api/quotes')
        assert quotes_response.status_code == 200
        initial_quotes = json.loads(quotes_response.data)
        initial_total = initial_quotes['total']
        
        # 5. 添加名言
        new_quote_data = {
            'content': 'End-to-end testing ensures system reliability.',
            'author': 'E2E Tester'
        }
        headers = {'Authorization': f'Bearer {token}'}
        add_quote_response = client.post('/api/quotes',
                                       data=json.dumps(new_quote_data),
                                       content_type='application/json',
                                       headers=headers)
        assert add_quote_response.status_code == 201
        
        # 6. 验证名言已添加
        updated_quotes_response = client.get('/api/quotes')
        assert updated_quotes_response.status_code == 200
        updated_quotes = json.loads(updated_quotes_response.data)
        assert updated_quotes['total'] == initial_total + 1
        
        # 7. 验证新名言内容
        new_quote_found = False
        for quote in updated_quotes['quotes']:
            if quote['content'] == new_quote_data['content']:
                assert quote['author'] == new_quote_data['author']
                new_quote_found = True
                break
        assert new_quote_found, "新添加的名言未找到"
        
        # 8. 最终系统健康检查
        final_health_response = client.get('/health/detailed')
        assert final_health_response.status_code == 200
        health_data = json.loads(final_health_response.data)
        assert health_data['status'] == 'healthy'
    
    def test_pagination_workflow(self, client):
        """测试分页功能完整流程"""
        # 1. 获取第一页
        page1_response = client.get('/api/quotes?page=1&page_size=5')
        assert page1_response.status_code == 200
        page1_data = json.loads(page1_response.data)
        
        # 2. 检查分页信息
        assert 'quotes' in page1_data
        assert 'total' in page1_data
        assert 'page' in page1_data
        assert 'page_size' in page1_data
        assert 'total_pages' in page1_data
        
        if page1_data['total_pages'] > 1:
            # 3. 获取第二页
            page2_response = client.get('/api/quotes?page=2&page_size=5')
            assert page2_response.status_code == 200
            page2_data = json.loads(page2_response.data)
            
            # 4. 验证页面数据不同
            page1_ids = [q['id'] for q in page1_data['quotes']]
            page2_ids = [q['id'] for q in page2_data['quotes']]
            assert set(page1_ids).isdisjoint(set(page2_ids)), "分页数据重复"
    
    def test_error_handling_workflow(self, client):
        """测试错误处理流程"""
        # 1. 测试未授权访问
        unauthorized_data = {
            'content': 'This should fail',
            'author': 'Unauthorized User'
        }
        response = client.post('/api/quotes',
                             data=json.dumps(unauthorized_data),
                             content_type='application/json')
        assert response.status_code == 401
        
        # 2. 测试无效token
        invalid_headers = {'Authorization': 'Bearer invalid_token_123'}
        response = client.post('/api/quotes',
                             data=json.dumps(unauthorized_data),
                             content_type='application/json',
                             headers=invalid_headers)
        assert response.status_code == 422  # Invalid token format
        
        # 3. 测试缺失字段
        incomplete_data = {'content': 'Missing author field'}
        # 首先注册用户获取有效token
        import time
        unique_suffix = str(int(time.time()))
        register_data = {'username': f'error_test_user_{unique_suffix}', 'password': 'password123'}
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(register_data),
                                      content_type='application/json')
        token = json.loads(register_response.data)['token']
        
        valid_headers = {'Authorization': f'Bearer {token}'}
        response = client.post('/api/quotes',
                             data=json.dumps(incomplete_data),
                             content_type='application/json',
                             headers=valid_headers)
        assert response.status_code == 400
    
    def test_concurrent_user_operations(self, client):
        """测试并发用户操作"""
        import time
        import threading
        base_timestamp = int(time.time())
        results = []
        errors = []

        def register_user(username):
            try:
                # 每个线程创建自己的测试客户端以避免context问题
                with app.test_client() as thread_client:
                    register_data = {
                        'username': f'concurrent_user_{base_timestamp}_{username}',
                        'password': 'password123'
                    }
                    response = thread_client.post('/api/auth/register',
                                         data=json.dumps(register_data),
                                         content_type='application/json')
                    results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # 创建多个并发注册请求
        threads = []
        for i in range(5):
            thread = threading.Thread(target=register_user, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(errors) == 0, f"并发操作出现错误: {errors}"
        assert len(results) == 5
        assert all(status in [201, 409] for status in results), f"注册状态码异常: {results}"
    
    def test_system_resilience(self, client):
        """测试系统韧性"""
        import time
        # 1. 大量快速请求测试
        start_time = time.time()
        responses = []

        for i in range(10):
            response = client.get('/health')
            responses.append(response.status_code)

        end_time = time.time()
        total_time = end_time - start_time

        # 验证所有请求成功且响应时间合理
        assert all(status == 200 for status in responses)
        assert total_time < 5.0, f"10个健康检查请求耗时过长: {total_time}秒"

        # 2. 测试长内容处理
        long_content = "A" * 1000  # 1000字符的长内容
        unique_suffix = str(int(time.time()))
        register_data = {'username': f'resilience_user_{unique_suffix}', 'password': 'password123'}
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(register_data),
                                      content_type='application/json')
        token = json.loads(register_response.data)['token']
        
        long_quote_data = {
            'content': long_content,
            'author': 'Long Content Author'
        }
        headers = {'Authorization': f'Bearer {token}'}
        response = client.post('/api/quotes',
                             data=json.dumps(long_quote_data),
                             content_type='application/json',
                             headers=headers)
        assert response.status_code in [201, 400]  # 成功或因长度限制失败
    
    def test_api_consistency(self, client):
        """测试API一致性"""
        # 1. 测试所有端点返回JSON
        endpoints = ['/health', '/health/detailed', '/status', '/version', '/api/quotes']
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 401], f"{endpoint} 返回异常状态码"
            assert response.content_type.startswith('application/json'), f"{endpoint} 未返回JSON"
        
        # 2. 测试错误响应格式一致性
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404
        assert response.content_type.startswith('application/json')
        
        error_data = json.loads(response.data)
        assert 'message' in error_data, "错误响应缺少message字段"


class TestDeploymentValidation:
    """部署验证测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_deployment_readiness_check(self, client):
        """测试部署就绪性检查"""
        # 1. 健康检查端点必须可用
        health_response = client.get('/health')
        assert health_response.status_code == 200
        
        health_data = json.loads(health_response.data)
        required_fields = ['status', 'timestamp', 'service', 'version']
        for field in required_fields:
            assert field in health_data, f"健康检查缺少必需字段: {field}"
        
        # 2. 详细健康检查必须包含核心检查项
        detailed_response = client.get('/health/detailed')
        assert detailed_response.status_code in [200, 503]
        
        detailed_data = json.loads(detailed_response.data)
        assert 'checks' in detailed_data
        assert 'database' in detailed_data['checks']
        assert 'jwt' in detailed_data['checks']
        
        # 3. 系统状态端点必须提供配置信息
        status_response = client.get('/status')
        assert status_response.status_code == 200
        
        status_data = json.loads(status_response.data)
        required_sections = ['environment', 'database', 'configuration']
        for section in required_sections:
            assert section in status_data, f"系统状态缺少必需部分: {section}"
        
        # 4. 版本信息必须可用
        version_response = client.get('/version')
        assert version_response.status_code == 200
        
        version_data = json.loads(version_response.data)
        version_fields = ['service', 'version', 'python_version', 'environment']
        for field in version_fields:
            assert field in version_data, f"版本信息缺少必需字段: {field}"
    
    def test_core_api_functionality(self, client):
        """测试核心API功能"""
        # 1. 根端点可用
        root_response = client.get('/')
        assert root_response.status_code == 200
        
        # 2. 名言列表端点可用
        quotes_response = client.get('/api/quotes')
        assert quotes_response.status_code == 200
        
        quotes_data = json.loads(quotes_response.data)
        assert 'quotes' in quotes_data
        assert isinstance(quotes_data['quotes'], list)
        
        # 3. 认证端点可用（注册）
        test_user = {
            'username': f'deploy_test_user_{int(time.time())}',
            'password': 'test_password_123'
        }
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(test_user),
                                      content_type='application/json')
        assert register_response.status_code == 201
        
        # 4. 认证端点可用（登录）
        login_response = client.post('/api/auth/login',
                                   data=json.dumps(test_user),
                                   content_type='application/json')
        assert login_response.status_code == 200
    
    def test_performance_baseline(self, client):
        """测试性能基准"""
        # 1. 健康检查响应时间
        start_time = time.time()
        response = client.get('/health')
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = (end_time - start_time) * 1000  # 转换为毫秒
        assert response_time < 500, f"健康检查响应时间过长: {response_time}ms"
        
        # 2. API响应时间
        start_time = time.time()
        response = client.get('/api/quotes')
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = (end_time - start_time) * 1000
        assert response_time < 1000, f"API响应时间过长: {response_time}ms"

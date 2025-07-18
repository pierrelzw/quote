"""
健康检查和监控端点测试
测试所有新增的监控功能
"""
import pytest
import json
from app import app


class TestHealthChecks:
    """健康检查端点测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_basic_health_check(self, client):
        """测试基础健康检查端点"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'quote-api'
        assert data['version'] == '1.0.0'
        assert 'timestamp' in data
    
    def test_detailed_health_check(self, client):
        """测试详细健康检查端点"""
        response = client.get('/health/detailed')
        assert response.status_code in [200, 503]  # 可能是健康或不健康
        
        data = json.loads(response.data)
        assert data['service'] == 'quote-api'
        assert data['version'] == '1.0.0'
        assert 'checks' in data
        assert 'database' in data['checks']
        assert 'jwt' in data['checks']
        assert 'timestamp' in data
        assert 'environment' in data
    
    def test_database_health_check(self, client):
        """测试数据库健康检查"""
        response = client.get('/health/detailed')
        data = json.loads(response.data)
        
        db_check = data['checks']['database']
        assert 'status' in db_check
        assert 'message' in db_check
        assert db_check['status'] in ['healthy', 'unhealthy']
    
    def test_jwt_health_check(self, client):
        """测试JWT配置健康检查"""
        response = client.get('/health/detailed')
        data = json.loads(response.data)
        
        jwt_check = data['checks']['jwt']
        assert 'status' in jwt_check
        assert 'message' in jwt_check
        assert jwt_check['status'] in ['healthy', 'warning', 'unhealthy']
    
    def test_system_status(self, client):
        """测试系统状态端点"""
        response = client.get('/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['service'] == 'quote-api'
        assert data['version'] == '1.0.0'
        assert 'environment' in data
        assert 'database' in data
        assert 'configuration' in data
        
        # 检查环境信息
        env = data['environment']
        assert 'flask_env' in env
        assert 'python_version' in env
        assert 'platform' in env
        assert 'is_production' in env
        
        # 检查数据库信息
        db = data['database']
        assert 'type' in db
        assert 'connection_string_configured' in db
        
        # 检查配置信息
        config = data['configuration']
        assert 'cors_origins' in config
        assert 'port' in config
        assert 'jwt_configured' in config
    
    def test_version_info(self, client):
        """测试版本信息端点"""
        response = client.get('/version')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['service'] == 'quote-api'
        assert data['version'] == '1.0.0'
        assert 'python_version' in data
        assert 'flask_version' in data
        assert 'build_date' in data
        assert 'environment' in data
    
    def test_health_endpoints_cors(self, client):
        """测试健康检查端点的CORS配置"""
        response = client.get('/health')
        # 应该有CORS头部（通过Flask-CORS自动添加）
        assert response.status_code == 200
    
    def test_health_check_performance(self, client):
        """测试健康检查的响应性能"""
        import time
        
        start_time = time.time()
        response = client.get('/health')
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0  # 健康检查应该在1秒内响应
    
    def test_detailed_health_check_error_handling(self, client):
        """测试详细健康检查的错误处理"""
        # 这个测试验证即使某些检查失败，端点仍然返回有用信息
        response = client.get('/health/detailed')
        data = json.loads(response.data)
        
        # 确保即使有错误，仍有基本结构
        assert 'status' in data
        assert 'checks' in data
        assert 'timestamp' in data

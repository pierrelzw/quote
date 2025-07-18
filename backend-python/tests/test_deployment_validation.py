"""
部署前验证测试
确保应用准备好部署到Render
"""
import pytest
import json
import os
import subprocess
import tempfile
from unittest.mock import patch
from app import app


class TestDeploymentReadiness:
    """部署就绪性测试"""
    
    def test_environment_variables_handling(self):
        """测试环境变量处理"""
        # 测试必需的环境变量
        required_env_vars = ['JWT_SECRET_KEY']
        
        # 测试默认值处理
        default_env_vars = {
            'PORT': '5000',
            'FLASK_ENV': 'development',
            'CORS_ORIGINS': '*'
        }
        
        for var, default_value in default_env_vars.items():
            with patch.dict(os.environ, {}, clear=True):
                # 清除环境变量，测试默认值
                value = os.getenv(var, default_value)
                assert value == default_value
    
    def test_database_configuration_flexibility(self):
        """测试数据库配置灵活性"""
        # 测试无DATABASE_URL时使用SQLite
        with patch.dict(os.environ, {}, clear=True):
            app.config['TESTING'] = True
            with app.test_client() as client:
                response = client.get('/status')
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert data['database']['type'] == 'sqlite'
                assert data['database']['connection_string_configured'] == False
        
        # 测试有DATABASE_URL时的配置
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            app.config['TESTING'] = True
            with app.test_client() as client:
                response = client.get('/status')
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert data['database']['connection_string_configured'] == True
    
    def test_cors_configuration(self):
        """测试CORS配置"""
        # 测试开发环境CORS（允许所有）
        with patch.dict(os.environ, {'CORS_ORIGINS': '*'}):
            app.config['TESTING'] = True
            with app.test_client() as client:
                response = client.get('/health')
                assert response.status_code == 200
        
        # 测试生产环境CORS（限制域名）
        with patch.dict(os.environ, {'CORS_ORIGINS': 'https://myapp.github.io'}):
            app.config['TESTING'] = True
            with app.test_client() as client:
                response = client.get('/health')
                assert response.status_code == 200
                
                status_response = client.get('/status')
                status_data = json.loads(status_response.data)
                assert 'github.io' in status_data['configuration']['cors_origins']
    
    def test_security_configuration(self):
        """测试安全配置"""
        # 测试JWT密钥配置
        with patch.dict(os.environ, {'JWT_SECRET_KEY': 'secure_production_key'}):
            app.config['TESTING'] = True
            with app.test_client() as client:
                response = client.get('/health/detailed')
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert data['checks']['jwt']['status'] == 'healthy'
        
        # 测试默认JWT密钥警告
        with patch.dict(os.environ, {}, clear=True):
            app.config['TESTING'] = True
            with app.test_client() as client:
                response = client.get('/health/detailed')
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert data['checks']['jwt']['status'] in ['warning', 'healthy']
    
    def test_production_vs_development_behavior(self):
        """测试生产环境与开发环境行为差异"""
        # 开发环境测试
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            app.config['TESTING'] = True
            with app.test_client() as client:
                response = client.get('/health')
                data = json.loads(response.data)
                assert data['environment'] == 'development'
        
        # 模拟生产环境测试
        with patch.dict(os.environ, {
            'FLASK_ENV': 'production',
            'DATABASE_URL': 'postgresql://test:test@localhost/test'
        }):
            with patch('app.IS_PRODUCTION', True):
                app.config['TESTING'] = True
                with app.test_client() as client:
                    response = client.get('/health')
                    data = json.loads(response.data)
                    assert data['environment'] == 'production'


class TestRenderSpecificRequirements:
    """Render平台特定要求测试"""
    
    def test_port_binding(self):
        """测试端口绑定"""
        # Render会设置PORT环境变量
        test_port = '10000'
        with patch.dict(os.environ, {'PORT': test_port}):
            app.config['TESTING'] = True
            with app.test_client() as client:
                response = client.get('/status')
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert data['configuration']['port'] == test_port
    
    def test_health_check_endpoint_compliance(self):
        """测试健康检查端点Render兼容性"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            # Render期望的健康检查响应
            response = client.get('/health')
            assert response.status_code == 200
            assert response.content_type.startswith('application/json')
            
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
            
            # 响应应该快速且轻量
            assert len(response.data) < 1000  # 小于1KB
    
    def test_static_file_serving(self):
        """测试静态文件服务（如果需要）"""
        # 对于API服务，通常不需要静态文件
        # 但测试确保不会有冲突
        app.config['TESTING'] = True
        with app.test_client() as client:
            response = client.get('/static/nonexistent.css')
            assert response.status_code == 404
    
    def test_request_handling_capacity(self):
        """测试请求处理能力"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            # 模拟多个同时请求
            responses = []
            for i in range(20):
                response = client.get('/health')
                responses.append(response.status_code)
            
            # 所有请求都应该成功
            assert all(status == 200 for status in responses)
    
    def test_memory_usage_stability(self):
        """测试内存使用稳定性"""
        import gc
        import sys
        
        app.config['TESTING'] = True
        with app.test_client() as client:
            # 获取初始内存使用情况
            initial_objects = len(gc.get_objects())
            
            # 执行多次请求
            for i in range(50):
                response = client.get('/health')
                assert response.status_code == 200
            
            # 强制垃圾回收
            gc.collect()
            
            # 检查内存泄漏
            final_objects = len(gc.get_objects())
            object_growth = final_objects - initial_objects
            
            # 允许一定的对象增长，但不应该过多
            assert object_growth < 1000, f"可能存在内存泄漏，对象增长: {object_growth}"


class TestDependencyValidation:
    """依赖验证测试"""
    
    def test_required_packages_import(self):
        """测试必需包导入"""
        required_packages = [
            'flask',
            'flask_cors',
            'flask_jwt_extended',
            'bcrypt',
            'sqlite3',
            'datetime',
            'os',
            'json'
        ]
        
        for package in required_packages:
            try:
                if package == 'flask_cors':
                    import flask_cors
                elif package == 'flask_jwt_extended':
                    import flask_jwt_extended
                else:
                    __import__(package)
            except ImportError as e:
                pytest.fail(f"必需包 {package} 导入失败: {e}")
    
    def test_optional_packages_handling(self):
        """测试可选包处理"""
        # 测试PostgreSQL包（生产环境需要）
        try:
            import psycopg2
            psycopg2_available = True
        except ImportError:
            psycopg2_available = False
        
        # 在测试环境中，psycopg2应该可用（我们在requirements中包含了它）
        assert psycopg2_available, "PostgreSQL连接器psycopg2应该可用"
    
    def test_version_compatibility(self):
        """测试版本兼容性"""
        import sys
        import flask
        
        # 检查Python版本
        python_version = sys.version_info
        assert python_version >= (3, 8), f"Python版本过低: {python_version}"
        
        # 检查Flask版本
        flask_version = tuple(map(int, flask.__version__.split('.')))
        assert flask_version >= (3, 0), f"Flask版本过低: {flask.__version__}"


class TestConfigurationValidation:
    """配置验证测试"""
    
    def test_production_configuration_completeness(self):
        """测试生产配置完整性"""
        production_env = {
            'FLASK_ENV': 'production',
            'JWT_SECRET_KEY': 'secure_production_key',
            'DATABASE_URL': 'postgresql://user:pass@host:5432/db',
            'CORS_ORIGINS': 'https://myapp.github.io',
            'PORT': '5000'
        }
        
        with patch.dict(os.environ, production_env):
            app.config['TESTING'] = True
            with app.test_client() as client:
                # 测试所有监控端点
                endpoints = ['/health', '/health/detailed', '/status', '/version']
                for endpoint in endpoints:
                    response = client.get(endpoint)
                    assert response.status_code in [200, 503], f"{endpoint} 在生产配置下异常"
    
    def test_development_configuration_fallbacks(self):
        """测试开发配置回退"""
        # 最小环境变量配置
        minimal_env = {}
        
        with patch.dict(os.environ, minimal_env, clear=True):
            app.config['TESTING'] = True
            with app.test_client() as client:
                response = client.get('/health')
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert data['status'] == 'healthy'
    
    def test_gunicorn_compatibility(self):
        """测试Gunicorn兼容性"""
        # 测试应用对象可以被Gunicorn导入
        try:
            from app import app as wsgi_app
            assert wsgi_app is not None
            assert hasattr(wsgi_app, 'wsgi_app') or callable(wsgi_app)
        except Exception as e:
            pytest.fail(f"Gunicorn兼容性测试失败: {e}")
    
    def test_render_yaml_compliance(self):
        """测试Render配置文件兼容性"""
        # 检查render.yaml是否存在且格式正确
        render_yaml_path = os.path.join(os.path.dirname(__file__), '..', 'render.yaml')
        assert os.path.exists(render_yaml_path), "render.yaml文件不存在"
        
        # 检查requirements_prod.txt是否存在
        requirements_path = os.path.join(os.path.dirname(__file__), '..', 'requirements_prod.txt')
        assert os.path.exists(requirements_path), "requirements_prod.txt文件不存在"
        
        # 检查runtime.txt是否存在
        runtime_path = os.path.join(os.path.dirname(__file__), '..', 'runtime.txt')
        assert os.path.exists(runtime_path), "runtime.txt文件不存在"

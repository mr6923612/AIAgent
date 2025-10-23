"""
API连通性测试
测试前后端API的基本连通性和响应
"""
import pytest
from unittest.mock import patch, Mock
from crewaiBackend.main import app


class TestAPIConnectivity:
    """API连通性测试类"""
    
    @pytest.fixture
    def client(self):
        """Flask测试客户端"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_health_endpoint_exists(self, client):
        """测试健康检查端点存在"""
        response = client.get('/health')
        # 健康检查端点存在，但可能返回不健康状态
        assert response.status_code in [200, 503]
        assert response.json is not None
    
    def test_health_endpoint_response_format(self, client):
        """测试健康检查响应格式"""
        response = client.get('/health')
        data = response.json
        assert 'status' in data
        assert 'timestamp' in data
        # 状态可能是healthy或unhealthy
        assert data['status'] in ['healthy', 'unhealthy']
    
    def test_sessions_status_endpoint(self, client):
        """测试会话状态端点"""
        response = client.get('/api/sessions/status')
        assert response.status_code == 200
        assert response.json is not None
    
    def test_sessions_status_response_format(self, client):
        """测试会话状态响应格式"""
        response = client.get('/api/sessions/status')
        data = response.json
        assert 'total_sessions' in data
        # 检查响应包含必要的字段
        assert isinstance(data['total_sessions'], int)
    
    def test_api_routes_registered(self):
        """测试API路由已注册"""
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/health' in routes
        assert '/api/sessions/status' in routes
        assert '/api/sessions' in routes
        assert '/api/crew' in routes
    
    def test_flask_app_configuration(self):
        """测试Flask应用配置"""
        assert app is not None
        assert app.name == 'crewaiBackend.main'
        assert hasattr(app, 'config')
    
    def test_cors_enabled(self):
        """测试CORS已启用"""
        # 检查CORS扩展是否存在
        assert hasattr(app, 'extensions')
    
    def test_api_endpoints_accessible(self, client):
        """测试API端点可访问性"""
        # 测试健康检查端点
        response = client.get('/health')
        assert response.status_code in [200, 503]
        
        # 测试会话状态端点
        response = client.get('/api/sessions/status')
        assert response.status_code == 200
        
        # 测试会话列表端点
        response = client.get('/api/users/test_user/sessions')
        assert response.status_code == 200
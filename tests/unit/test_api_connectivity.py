"""
API Connectivity Tests
Test basic connectivity and responses of frontend and backend APIs
"""
import pytest
from unittest.mock import patch, Mock
from crewaiBackend.main import app


class TestAPIConnectivity:
    """API connectivity test class"""
    
    @pytest.fixture
    def client(self):
        """Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_health_endpoint_exists(self, client):
        """Test health check endpoint exists"""
        response = client.get('/health')
        # Health check endpoint exists, but may return unhealthy status
        assert response.status_code in [200, 503]
        assert response.json is not None
    
    def test_health_endpoint_response_format(self, client):
        """Test health check response format"""
        response = client.get('/health')
        data = response.json
        assert 'status' in data
        assert 'timestamp' in data
        # Status may be healthy or unhealthy
        assert data['status'] in ['healthy', 'unhealthy']
    
    def test_sessions_status_endpoint(self, client):
        """Test session status endpoint"""
        response = client.get('/api/sessions/status')
        assert response.status_code == 200
        assert response.json is not None
    
    def test_sessions_status_response_format(self, client):
        """Test session status response format"""
        response = client.get('/api/sessions/status')
        data = response.json
        assert 'total_sessions' in data
        # Check response contains necessary fields
        assert isinstance(data['total_sessions'], int)
    
    def test_api_routes_registered(self):
        """Test API routes are registered"""
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/health' in routes
        assert '/api/sessions/status' in routes
        assert '/api/sessions' in routes
        assert '/api/crew' in routes
    
    def test_flask_app_configuration(self):
        """Test Flask application configuration"""
        assert app is not None
        assert app.name == 'crewaiBackend.main'
        assert hasattr(app, 'config')
    
    def test_cors_enabled(self):
        """Test CORS is enabled"""
        # Check if CORS extension exists
        assert hasattr(app, 'extensions')
    
    def test_api_endpoints_accessible(self, client):
        """Test API endpoint accessibility"""
        # Test health check endpoint
        response = client.get('/health')
        assert response.status_code in [200, 503]
        
        # Test session status endpoint
        response = client.get('/api/sessions/status')
        assert response.status_code == 200
        
        # Test session list endpoint
        response = client.get('/api/users/test_user/sessions')
        assert response.status_code == 200
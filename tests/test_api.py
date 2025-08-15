import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

class TestHealthEndpoints:
    """Test health and status endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ZeusAI Orchestrator"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"
    
    def test_health_endpoint(self, client, mock_redis, mock_mcp_client):
        """Test health check endpoint."""
        mock_redis.ping.return_value = True
        mock_mcp_client.return_value.get_services_status.return_value = {
            "obs-mcp": "healthy",
            "k8s-mcp": "healthy"
        }
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["redis"] == "connected"

class TestInfrastructureAPI:
    """Test infrastructure endpoints."""
    
    def test_create_infrastructure(self, client, admin_user, mock_mcp_client):
        """Test infrastructure creation."""
        mock_mcp_client.return_value.generate_terraform.return_value = "terraform code"
        mock_mcp_client.return_value.create_infrastructure_pr.return_value = "https://github.com/pr/123"
        
        infrastructure_data = {
            "name": "test-infra",
            "environment": "development",
            "cloud_provider": "aws",
            "components": [
                {
                    "name": "web-server",
                    "type": "ec2",
                    "configuration": {"instance_type": "t3.micro"}
                }
            ],
            "created_by": admin_user.id
        }
        
        response = client.post("/api/v1/infrastructure/", json=infrastructure_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test-infra"
        assert data["environment"] == "development"
    
    def test_list_infrastructure(self, client, sample_infrastructure):
        """Test infrastructure listing."""
        response = client.get("/api/v1/infrastructure/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(infra["name"] == sample_infrastructure.name for infra in data)
    
    def test_get_infrastructure(self, client, sample_infrastructure):
        """Test getting specific infrastructure."""
        response = client.get(f"/api/v1/infrastructure/{sample_infrastructure.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_infrastructure.name
        assert data["id"] == sample_infrastructure.id
    
    def test_get_infrastructure_not_found(self, client):
        """Test getting non-existent infrastructure."""
        response = client.get("/api/v1/infrastructure/999999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_deploy_infrastructure(self, client, sample_infrastructure, mock_mcp_client):
        """Test infrastructure deployment."""
        mock_mcp_client.return_value.execute_command.return_value = {"success": True}
        
        response = client.post(f"/api/v1/infrastructure/{sample_infrastructure.id}/deploy")
        assert response.status_code == 200
        data = response.json()
        assert "deployment started" in data["message"]

class TestObservabilityAPI:
    """Test observability endpoints."""
    
    def test_query_observability(self, client, mock_mcp_client):
        """Test observability query."""
        mock_mcp_client.return_value.query_observability.return_value = {
            "metrics": [{"name": "cpu", "value": 75.2}]
        }
        
        query_data = {
            "query": "cpu_usage",
            "start_time": "2024-01-01T00:00:00Z",
            "end_time": "2024-01-01T23:59:59Z"
        }
        
        response = client.post("/api/v1/observability/query", json=query_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "metrics" in data["data"]
    
    def test_get_metrics(self, client, mock_mcp_client):
        """Test metrics endpoint."""
        mock_mcp_client.return_value.query_observability.return_value = {
            "metrics": [{"name": "cpu", "value": 75.2}]
        }
        
        response = client.get("/api/v1/observability/metrics?query=cpu_usage")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_alerts(self, client, mock_mcp_client):
        """Test alerts endpoint."""
        mock_mcp_client.return_value.execute_command.return_value = {
            "alerts": [{"severity": "warning", "message": "High CPU"}]
        }
        
        response = client.get("/api/v1/observability/alerts")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "alerts" in data

class TestUsersAPI:
    """Test user management endpoints."""
    
    def test_list_users(self, client, admin_user):
        """Test user listing."""
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(user["username"] == admin_user.username for user in data)
    
    def test_get_user(self, client, admin_user):
        """Test getting specific user."""
        response = client.get(f"/api/v1/users/{admin_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == admin_user.username
        assert data["email"] == admin_user.email
    
    def test_create_user(self, client):
        """Test user creation."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword",
            "full_name": "New User",
            "role": "dev"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
    
    def test_create_duplicate_user(self, client, admin_user):
        """Test creating user with duplicate username."""
        user_data = {
            "username": admin_user.username,
            "email": "different@example.com",
            "password": "securepassword",
            "role": "dev"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

class TestDeploymentsAPI:
    """Test deployment endpoints."""
    
    def test_list_deployments(self, client):
        """Test deployment listing."""
        response = client.get("/api/v1/deployments/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deployments" in data
    
    def test_create_deployment(self, client, mock_mcp_client):
        """Test deployment creation."""
        mock_mcp_client.return_value.execute_command.return_value = {
            "deployment_id": "deploy-123"
        }
        
        deployment_data = {
            "name": "test-deployment",
            "environment": "staging",
            "image": "nginx:latest"
        }
        
        response = client.post("/api/v1/deployments/", json=deployment_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deployment_id" in data
    
    def test_get_deployment(self, client):
        """Test getting specific deployment."""
        response = client.get("/api/v1/deployments/deploy-123")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deployment" in data
    
    def test_rollback_deployment(self, client, mock_mcp_client):
        """Test deployment rollback."""
        mock_mcp_client.return_value.execute_command.return_value = {"success": True}
        
        response = client.post("/api/v1/deployments/deploy-123/rollback")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

class TestCostsAPI:
    """Test cost management endpoints."""
    
    def test_get_current_costs(self, client, mock_mcp_client):
        """Test current costs endpoint."""
        mock_mcp_client.return_value.execute_command.return_value = {
            "monthly_cost": 2450.75
        }
        
        response = client.get("/api/v1/costs/current")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "costs" in data
    
    def test_get_usage_metrics(self, client, mock_mcp_client):
        """Test usage metrics endpoint."""
        mock_mcp_client.return_value.execute_command.return_value = {
            "instances": 12,
            "storage_gb": 500
        }
        
        response = client.get("/api/v1/costs/usage")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "usage" in data
    
    def test_get_cost_forecast(self, client):
        """Test cost forecast endpoint."""
        response = client.get("/api/v1/costs/forecast")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "forecast" in data
    
    def test_get_cost_breakdown(self, client):
        """Test cost breakdown endpoint."""
        response = client.get("/api/v1/costs/breakdown")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "breakdown" in data

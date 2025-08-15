import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.core.guardrails import GuardrailEngine, GuardrailResult
from app.core.audit import AuditLogger
from app.core.websocket_manager import WebSocketManager
from app.core.mcp_client import MCPClient
import json

class TestGuardrailEngine:
    """Test guardrail functionality."""
    
    @pytest.fixture
    def guardrail_engine(self):
        return GuardrailEngine()
    
    @pytest.mark.asyncio
    async def test_validate_command_allowed(self, guardrail_engine):
        """Test command validation when allowed."""
        params = {
            "environment": "development",
            "user_role": "admin",
            "instances": 5
        }
        
        result = await guardrail_engine.validate_command("scale", params)
        assert result.allowed is True
        assert result.reason is None
    
    @pytest.mark.asyncio
    async def test_validate_command_blocked_scaling_limit(self, guardrail_engine):
        """Test command blocked by scaling limit."""
        params = {
            "environment": "development",
            "user_role": "admin",
            "instances": 200  # Exceeds limit
        }
        
        result = await guardrail_engine.validate_command("scale", params)
        assert result.allowed is False
        assert "exceeds limit" in result.reason
    
    @pytest.mark.asyncio
    async def test_validate_command_blocked_rbac(self, guardrail_engine):
        """Test command blocked by RBAC."""
        params = {
            "environment": "development",
            "user_role": "viewer",
            "instances": 5
        }
        
        result = await guardrail_engine.validate_command("scale", params)
        assert result.allowed is False
        assert "permission" in result.reason
    
    @pytest.mark.asyncio
    async def test_validate_design_allowed(self, guardrail_engine):
        """Test design validation when allowed."""
        design = {
            "environment": "development",
            "components": [
                {
                    "type": "ec2",
                    "count": 2,
                    "memory_gb": 4,
                    "cpu_cores": 2
                }
            ]
        }
        
        result = await guardrail_engine.validate_design(design)
        assert result.allowed is True
    
    @pytest.mark.asyncio
    async def test_validate_design_blocked_resource_limit(self, guardrail_engine):
        """Test design blocked by resource limit."""
        design = {
            "environment": "development",
            "components": [
                {
                    "type": "ec2",
                    "count": 200,  # Exceeds limit
                    "memory_gb": 4,
                    "cpu_cores": 2
                }
            ]
        }
        
        result = await guardrail_engine.validate_design(design)
        assert result.allowed is False
        assert "exceeds limit" in result.reason

class TestAuditLogger:
    """Test audit logging functionality."""
    
    @pytest.fixture
    def audit_logger(self):
        return AuditLogger()
    
    @pytest.mark.asyncio
    async def test_log_command(self, audit_logger, db_session):
        """Test command logging."""
        user_id = "test-user"
        command = "scale"
        params = {"instances": 5}
        result = {"success": True}
        
        await audit_logger.log_command(user_id, command, params, result)
        
        # Verify log was created
        from app.models.audit import CommandLog
        logs = db_session.query(CommandLog).filter(CommandLog.user_id == user_id).all()
        assert len(logs) >= 1
        assert logs[-1].command == command
    
    @pytest.mark.asyncio
    async def test_log_design(self, audit_logger, db_session):
        """Test design logging."""
        user_id = "test-user"
        design = {"name": "test-infra"}
        terraform_code = "resource aws_instance..."
        pr_url = "https://github.com/pr/123"
        
        await audit_logger.log_design(user_id, design, terraform_code, pr_url)
        
        # Verify log was created
        from app.models.audit import AuditLog
        logs = db_session.query(AuditLog).filter(AuditLog.user_id == user_id).all()
        assert len(logs) >= 1
        assert logs[-1].action == "infrastructure_design"
    
    @pytest.mark.asyncio
    async def test_log_guardrail_violation(self, audit_logger, db_session):
        """Test guardrail violation logging."""
        user_id = "test-user"
        command = "scale"
        reason = "Exceeds limit"
        params = {"instances": 200}
        
        await audit_logger.log_guardrail_violation(user_id, command, reason, params)
        
        # Verify log was created
        from app.models.audit import AuditLog
        logs = db_session.query(AuditLog).filter(AuditLog.user_id == user_id).all()
        assert len(logs) >= 1
        assert logs[-1].action == "guardrail_violation"

class TestWebSocketManager:
    """Test WebSocket management functionality."""
    
    @pytest.fixture
    def ws_manager(self):
        return WebSocketManager()
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self, ws_manager):
        """Test WebSocket connection and disconnection."""
        mock_websocket = AsyncMock()
        
        await ws_manager.connect(mock_websocket)
        assert len(ws_manager.active_connections) == 1
        assert mock_websocket in ws_manager.active_connections
        
        await ws_manager.disconnect(mock_websocket)
        assert len(ws_manager.active_connections) == 0
        assert mock_websocket not in ws_manager.active_connections
    
    @pytest.mark.asyncio
    async def test_subscribe_unsubscribe(self, ws_manager):
        """Test channel subscription and unsubscription."""
        mock_websocket = AsyncMock()
        channel = "infrastructure"
        
        await ws_manager.connect(mock_websocket)
        await ws_manager.subscribe(mock_websocket, channel)
        
        assert channel in ws_manager.channel_subscriptions
        assert mock_websocket in ws_manager.channel_subscriptions[channel]
        
        await ws_manager.unsubscribe(mock_websocket, channel)
        assert mock_websocket not in ws_manager.channel_subscriptions[channel]
    
    @pytest.mark.asyncio
    async def test_broadcast_to_channel(self, ws_manager):
        """Test broadcasting to specific channel."""
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        channel = "alerts"
        message = "Test alert"
        
        await ws_manager.connect(mock_websocket1)
        await ws_manager.connect(mock_websocket2)
        await ws_manager.subscribe(mock_websocket1, channel)
        await ws_manager.subscribe(mock_websocket2, channel)
        
        await ws_manager.broadcast_to_channel(message, channel)
        
        mock_websocket1.send_text.assert_called_with(message)
        mock_websocket2.send_text.assert_called_with(message)
    
    @pytest.mark.asyncio
    async def test_send_infrastructure_update(self, ws_manager):
        """Test infrastructure update broadcasting."""
        mock_websocket = AsyncMock()
        update = {"type": "infrastructure", "status": "deployed"}
        
        await ws_manager.connect(mock_websocket)
        await ws_manager.subscribe(mock_websocket, "infrastructure")
        
        await ws_manager.send_infrastructure_update(update)
        
        # Verify message was sent with correct format
        mock_websocket.send_text.assert_called_once()
        sent_message = mock_websocket.send_text.call_args[0][0]
        message_data = json.loads(sent_message)
        assert message_data["type"] == "infrastructure_update"
        assert message_data["data"] == update

class TestMCPClient:
    """Test MCP client functionality."""
    
    @pytest.fixture
    def mcp_client(self):
        return MCPClient()
    
    @pytest.mark.asyncio
    async def test_initialize(self, mcp_client):
        """Test MCP client initialization."""
        await mcp_client.initialize()
        assert len(mcp_client.clients) > 0
        assert "obs-mcp" in mcp_client.clients
        assert "k8s-mcp" in mcp_client.clients
    
    @pytest.mark.asyncio
    async def test_get_services_status(self, mcp_client):
        """Test getting services status."""
        await mcp_client.initialize()
        
        # Mock the HTTP client responses
        for client in mcp_client.clients.values():
            client.get = AsyncMock()
            client.get.return_value.status_code = 200
        
        status = await mcp_client.get_services_status()
        assert len(status) > 0
        assert all(service_status in ["healthy", "unhealthy", "unreachable"] for service_status in status.values())
    
    @pytest.mark.asyncio
    async def test_route_command(self, mcp_client):
        """Test command routing."""
        # Test Kubernetes commands
        assert mcp_client._route_command("scale") == "k8s-mcp"
        assert mcp_client._route_command("rollout") == "k8s-mcp"
        
        # Test cloud commands
        assert mcp_client._route_command("cost") == "cloud-mcp"
        assert mcp_client._route_command("usage") == "cloud-mcp"
        
        # Test deployment commands
        assert mcp_client._route_command("deploy") == "deploy-mcp"
        assert mcp_client._route_command("helm") == "deploy-mcp"
        
        # Test unknown command
        assert mcp_client._route_command("unknown") is None
    
    @pytest.mark.asyncio
    async def test_execute_command(self, mcp_client):
        """Test command execution."""
        await mcp_client.initialize()
        
        # Mock the HTTP client
        mock_client = AsyncMock()
        mock_client.post.return_value.json.return_value = {"success": True}
        mock_client.post.return_value.raise_for_status = MagicMock()
        mcp_client.clients["k8s-mcp"] = mock_client
        
        result = await mcp_client.execute_command("scale", {"deployment": "web", "replicas": 3})
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_execute_command_unknown_service(self, mcp_client):
        """Test command execution with unknown service."""
        await mcp_client.initialize()
        
        with pytest.raises(ValueError, match="No MCP service found"):
            await mcp_client.execute_command("unknown_command", {})
    
    @pytest.mark.asyncio
    async def test_generate_terraform(self, mcp_client):
        """Test Terraform generation."""
        await mcp_client.initialize()
        
        # Mock the HTTP client
        mock_client = AsyncMock()
        mock_client.post.return_value.json.return_value = {"terraform_code": "resource aws_instance..."}
        mock_client.post.return_value.raise_for_status = MagicMock()
        mcp_client.clients["tf-migrator"] = mock_client
        
        design = {"components": [{"type": "ec2"}]}
        terraform_code = await mcp_client.generate_terraform(design)
        assert "resource aws_instance" in terraform_code
    
    @pytest.mark.asyncio
    async def test_create_infrastructure_pr(self, mcp_client):
        """Test PR creation."""
        await mcp_client.initialize()
        
        # Mock the HTTP client
        mock_client = AsyncMock()
        mock_client.post.return_value.json.return_value = {"pr_url": "https://github.com/pr/123"}
        mock_client.post.return_value.raise_for_status = MagicMock()
        mcp_client.clients["git-mcp"] = mock_client
        
        terraform_code = "resource aws_instance..."
        design = {"name": "test-infra"}
        pr_url = await mcp_client.create_infrastructure_pr(terraform_code, design)
        assert "github.com/pr/123" in pr_url

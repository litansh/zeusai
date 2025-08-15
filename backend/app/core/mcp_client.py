import httpx
import asyncio
import logging
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        self.services = settings.mcp_services
        self.clients = {}
        
    async def initialize(self):
        """Initialize HTTP clients for all MCP services"""
        for service_name, service_url in self.services.items():
            self.clients[service_name] = httpx.AsyncClient(
                base_url=service_url,
                timeout=30.0
            )
        logger.info(f"Initialized {len(self.clients)} MCP service clients")
    
    async def get_services_status(self) -> Dict[str, str]:
        """Get status of all MCP services"""
        status = {}
        for service_name, client in self.clients.items():
            try:
                response = await client.get("/health")
                status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception as e:
                logger.error(f"Failed to check {service_name} status: {e}")
                status[service_name] = "unreachable"
        return status
    
    async def execute_command(self, command: str, params: Dict) -> Dict:
        """Execute a command through the appropriate MCP service"""
        # Route command to appropriate service
        service = self._route_command(command)
        if not service:
            raise ValueError(f"No MCP service found for command: {command}")
        
        try:
            response = await self.clients[service].post("/execute", json={
                "command": command,
                "parameters": params
            })
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to execute command {command} on {service}: {e}")
            raise
    
    async def generate_terraform(self, design_request: Dict) -> str:
        """Generate Terraform code from design request"""
        try:
            response = await self.clients["tf-migrator"].post("/generate", json=design_request)
            response.raise_for_status()
            return response.json()["terraform_code"]
        except Exception as e:
            logger.error(f"Failed to generate Terraform: {e}")
            raise
    
    async def create_infrastructure_pr(self, terraform_code: str, design_request: Dict) -> str:
        """Create GitHub PR for infrastructure changes"""
        try:
            response = await self.clients["git-mcp"].post("/pr/create", json={
                "terraform_code": terraform_code,
                "design_request": design_request,
                "repo": settings.github_repo
            })
            response.raise_for_status()
            return response.json()["pr_url"]
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            raise
    
    async def get_infrastructure_state(self) -> Dict:
        """Get current infrastructure state"""
        try:
            response = await self.clients["cloud-mcp"].get("/state")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get infrastructure state: {e}")
            raise
    
    async def query_observability(self, query: Dict) -> Dict:
        """Query observability data"""
        try:
            response = await self.clients["obs-mcp"].post("/query", json=query)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to query observability: {e}")
            raise
    
    async def get_kb_context(self, query: str) -> List[Dict]:
        """Get relevant context from knowledge base"""
        try:
            response = await self.clients["kb-mcp"].post("/search", json={"query": query})
            response.raise_for_status()
            return response.json()["results"]
        except Exception as e:
            logger.error(f"Failed to get KB context: {e}")
            return []
    
    async def generate_ai_response(self, message: str, context: List[Dict]) -> str:
        """Generate AI response using OpenAI"""
        try:
            response = await self.clients["kb-mcp"].post("/generate", json={
                "message": message,
                "context": context
            })
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            return "I apologize, but I'm unable to generate a response at the moment."
    
    def _route_command(self, command: str) -> Optional[str]:
        """Route command to appropriate MCP service"""
        command_mapping = {
            # Kubernetes commands
            "scale": "k8s-mcp",
            "rollout": "k8s-mcp",
            "describe": "k8s-mcp",
            "get": "k8s-mcp",
            
            # Cloud commands
            "cost": "cloud-mcp",
            "usage": "cloud-mcp",
            "iam": "cloud-mcp",
            
            # Deployment commands
            "deploy": "deploy-mcp",
            "helm": "deploy-mcp",
            "argocd": "deploy-mcp",
            
            # Observability commands
            "metrics": "obs-mcp",
            "logs": "obs-mcp",
            "alerts": "obs-mcp",
            
            # SLO commands
            "slo": "slo-mcp",
            "threshold": "slo-mcp",
            
            # Git commands
            "pr": "git-mcp",
            "commit": "git-mcp",
            "merge": "git-mcp",
            
            # Terraform commands
            "import": "tf-migrator",
            "migrate": "tf-migrator",
            "export": "tf-migrator"
        }
        
        for cmd_prefix, service in command_mapping.items():
            if command.startswith(cmd_prefix):
                return service
        
        return None
    
    async def close(self):
        """Close all HTTP clients"""
        for client in self.clients.values():
            await client.aclose()
        logger.info("Closed all MCP service clients")

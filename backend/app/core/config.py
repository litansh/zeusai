from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "ZeusAI Orchestrator"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://zeusai:zeusai@postgres:5432/zeusai"
    
    # Redis
    redis_url: str = "redis://redis:6379"
    
    # AWS
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_default_region: str = "us-west-2"
    
    # GitHub
    github_token: Optional[str] = None
    github_repo: str = "your-org/zeusai-infra"
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # Telegram
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Qdrant
    qdrant_url: str = "http://qdrant:6333"
    
    # Prometheus
    prometheus_url: str = "http://prometheus:9090"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    
    # MCP Services
    mcp_services: dict = {
        "obs-mcp": "http://obs-mcp:8000",
        "k8s-mcp": "http://k8s-mcp:8000",
        "git-mcp": "http://git-mcp:8000",
        "cloud-mcp": "http://cloud-mcp:8000",
        "kb-mcp": "http://kb-mcp:8000",
        "deploy-mcp": "http://deploy-mcp:8000",
        "slo-mcp": "http://slo-mcp:8000",
        "tf-migrator": "http://tf-migrator:8000"
    }
    
    # Guardrails
    guardrails_config: dict = {
        "change_windows": {
            "production": {
                "allowed_hours": [2, 3, 4, 5],  # 2 AM to 5 AM UTC
                "timezone": "UTC"
            }
        },
        "rbac": {
            "admin": ["*"],
            "dev": ["read", "deploy"],
            "viewer": ["read"]
        },
        "scaling_limits": {
            "max_instances": 100,
            "max_memory_gb": 512,
            "max_cpu_cores": 64
        },
        "prod_lockdown": {
            "enabled": True,
            "required_approvals": 2
        }
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

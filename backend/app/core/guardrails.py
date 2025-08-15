import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass
from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class GuardrailResult:
    allowed: bool
    reason: Optional[str] = None
    warnings: List[str] = None
    suggestions: List[str] = None

class GuardrailEngine:
    def __init__(self):
        self.config = settings.guardrails_config
        
    async def initialize(self):
        """Initialize guardrail engine"""
        logger.info("Guardrail engine initialized")
    
    async def validate_command(self, command: str, params: Dict) -> GuardrailResult:
        """Validate a command against guardrails"""
        warnings = []
        suggestions = []
        
        # Check change windows
        if not await self._check_change_window(params.get("environment", "development")):
            return GuardrailResult(
                allowed=False,
                reason="Command blocked: Outside allowed change window for production environment"
            )
        
        # Check scaling limits
        if command.startswith("scale"):
            scaling_check = await self._check_scaling_limits(params)
            if not scaling_check.allowed:
                return scaling_check
        
        # Check RBAC permissions
        rbac_check = await self._check_rbac_permissions(
            params.get("user_role", "viewer"),
            command
        )
        if not rbac_check.allowed:
            return rbac_check
        
        # Check production lockdown
        if params.get("environment") == "production":
            lockdown_check = await self._check_production_lockdown(params)
            if not lockdown_check.allowed:
                return lockdown_check
        
        return GuardrailResult(
            allowed=True,
            warnings=warnings,
            suggestions=suggestions
        )
    
    async def validate_design(self, design_request: Dict) -> GuardrailResult:
        """Validate infrastructure design against guardrails"""
        warnings = []
        suggestions = []
        
        # Check resource limits
        total_instances = 0
        total_memory = 0
        total_cpu = 0
        
        for component in design_request.get("components", []):
            if component.get("type") == "ec2":
                total_instances += component.get("count", 1)
                total_memory += component.get("memory_gb", 0) * component.get("count", 1)
                total_cpu += component.get("cpu_cores", 0) * component.get("count", 1)
        
        # Check instance limits
        if total_instances > self.config["scaling_limits"]["max_instances"]:
            return GuardrailResult(
                allowed=False,
                reason=f"Total instances ({total_instances}) exceeds limit ({self.config['scaling_limits']['max_instances']})"
            )
        
        # Check memory limits
        if total_memory > self.config["scaling_limits"]["max_memory_gb"]:
            return GuardrailResult(
                allowed=False,
                reason=f"Total memory ({total_memory}GB) exceeds limit ({self.config['scaling_limits']['max_memory_gb']}GB)"
            )
        
        # Check CPU limits
        if total_cpu > self.config["scaling_limits"]["max_cpu_cores"]:
            return GuardrailResult(
                allowed=False,
                reason=f"Total CPU cores ({total_cpu}) exceeds limit ({self.config['scaling_limits']['max_cpu_cores']})"
            )
        
        # Check environment-specific rules
        environment = design_request.get("environment", "development")
        if environment == "production":
            # Production-specific checks
            if not design_request.get("backup_enabled", False):
                warnings.append("Backup is not enabled for production environment")
                suggestions.append("Enable backup for production infrastructure")
            
            if not design_request.get("monitoring_enabled", False):
                warnings.append("Monitoring is not enabled for production environment")
                suggestions.append("Enable monitoring for production infrastructure")
        
        return GuardrailResult(
            allowed=True,
            warnings=warnings,
            suggestions=suggestions
        )
    
    async def _check_change_window(self, environment: str) -> bool:
        """Check if current time is within allowed change window"""
        if environment != "production":
            return True
        
        change_windows = self.config.get("change_windows", {})
        if "production" not in change_windows:
            return True
        
        current_hour = datetime.now(timezone.utc).hour
        allowed_hours = change_windows["production"].get("allowed_hours", [])
        
        return current_hour in allowed_hours
    
    async def _check_scaling_limits(self, params: Dict) -> GuardrailResult:
        """Check scaling limits"""
        limits = self.config["scaling_limits"]
        
        # Check instance count
        if "instances" in params:
            if params["instances"] > limits["max_instances"]:
                return GuardrailResult(
                    allowed=False,
                    reason=f"Instance count ({params['instances']}) exceeds limit ({limits['max_instances']})"
                )
        
        # Check memory
        if "memory_gb" in params:
            if params["memory_gb"] > limits["max_memory_gb"]:
                return GuardrailResult(
                    allowed=False,
                    reason=f"Memory ({params['memory_gb']}GB) exceeds limit ({limits['max_memory_gb']}GB)"
                )
        
        # Check CPU
        if "cpu_cores" in params:
            if params["cpu_cores"] > limits["max_cpu_cores"]:
                return GuardrailResult(
                    allowed=False,
                    reason=f"CPU cores ({params['cpu_cores']}) exceeds limit ({limits['max_cpu_cores']})"
                )
        
        return GuardrailResult(allowed=True)
    
    async def _check_rbac_permissions(self, user_role: str, command: str) -> GuardrailResult:
        """Check RBAC permissions"""
        rbac_config = self.config.get("rbac", {})
        
        if user_role not in rbac_config:
            return GuardrailResult(
                allowed=False,
                reason=f"Unknown user role: {user_role}"
            )
        
        user_permissions = rbac_config[user_role]
        
        # Admin has all permissions
        if "*" in user_permissions:
            return GuardrailResult(allowed=True)
        
        # Check specific permissions
        if command.startswith("scale") and "scale" not in user_permissions:
            return GuardrailResult(
                allowed=False,
                reason=f"User role '{user_role}' does not have permission to scale resources"
            )
        
        if command.startswith("deploy") and "deploy" not in user_permissions:
            return GuardrailResult(
                allowed=False,
                reason=f"User role '{user_role}' does not have permission to deploy"
            )
        
        return GuardrailResult(allowed=True)
    
    async def _check_production_lockdown(self, params: Dict) -> GuardrailResult:
        """Check production lockdown rules"""
        lockdown_config = self.config.get("prod_lockdown", {})
        
        if not lockdown_config.get("enabled", False):
            return GuardrailResult(allowed=True)
        
        required_approvals = lockdown_config.get("required_approvals", 1)
        current_approvals = params.get("approvals", 0)
        
        if current_approvals < required_approvals:
            return GuardrailResult(
                allowed=False,
                reason=f"Production changes require {required_approvals} approvals, but only {current_approvals} provided"
            )
        
        return GuardrailResult(allowed=True)

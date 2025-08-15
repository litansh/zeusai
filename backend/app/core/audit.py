import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.audit import AuditLog, CommandLog

logger = logging.getLogger(__name__)

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("audit")
    
    async def log_command(self, user_id: str, command: str, params: Dict, result: Dict):
        """Log a command execution"""
        try:
            db = SessionLocal()
            command_log = CommandLog(
                user_id=user_id,
                command=command,
                parameters=params,
                result=result,
                success=result.get("success", True),
                error_message=result.get("error"),
                execution_time_ms=result.get("execution_time_ms", 0),
                timestamp=datetime.now(timezone.utc)
            )
            db.add(command_log)
            db.commit()
            db.close()
            
            self.logger.info(f"Command logged: {command} by user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log command: {e}")
    
    async def log_design(self, user_id: str, design: Dict, terraform_code: str, pr_url: str):
        """Log infrastructure design creation"""
        try:
            db = SessionLocal()
            audit_log = AuditLog(
                user_id=user_id,
                action="infrastructure_design",
                resource_type="infrastructure",
                details={
                    "design": design,
                    "terraform_code_length": len(terraform_code),
                    "pr_url": pr_url,
                    "environment": design.get("environment"),
                    "components_count": len(design.get("components", []))
                },
                timestamp=datetime.now(timezone.utc)
            )
            db.add(audit_log)
            db.commit()
            db.close()
            
            self.logger.info(f"Infrastructure design logged by user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log design: {e}")
    
    async def log_deployment(self, user_id: str, deployment: Dict, status: str):
        """Log deployment action"""
        try:
            db = SessionLocal()
            audit_log = AuditLog(
                user_id=user_id,
                action="deployment",
                resource_type="deployment",
                resource_id=deployment.get("id"),
                details={
                    "deployment": deployment,
                    "status": status,
                    "environment": deployment.get("environment")
                },
                timestamp=datetime.now(timezone.utc)
            )
            db.add(audit_log)
            db.commit()
            db.close()
            
            self.logger.info(f"Deployment logged: {status} by user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log deployment: {e}")
    
    async def log_guardrail_violation(self, user_id: str, command: str, reason: str, params: Dict):
        """Log guardrail violation"""
        try:
            db = SessionLocal()
            audit_log = AuditLog(
                user_id=user_id,
                action="guardrail_violation",
                resource_type="command",
                details={
                    "command": command,
                    "reason": reason,
                    "parameters": params,
                    "blocked": True
                },
                timestamp=datetime.now(timezone.utc)
            )
            db.add(audit_log)
            db.commit()
            db.close()
            
            self.logger.warning(f"Guardrail violation logged: {command} by user {user_id} - {reason}")
        except Exception as e:
            logger.error(f"Failed to log guardrail violation: {e}")
    
    async def log_cost_alert(self, alert: Dict):
        """Log cost alert"""
        try:
            db = SessionLocal()
            audit_log = AuditLog(
                user_id="system",
                action="cost_alert",
                resource_type="cost",
                details={
                    "alert": alert,
                    "threshold": alert.get("threshold"),
                    "current_cost": alert.get("current_cost"),
                    "period": alert.get("period")
                },
                timestamp=datetime.now(timezone.utc)
            )
            db.add(audit_log)
            db.commit()
            db.close()
            
            self.logger.warning(f"Cost alert logged: {alert.get('message')}")
        except Exception as e:
            logger.error(f"Failed to log cost alert: {e}")
    
    async def log_observability_alert(self, alert: Dict):
        """Log observability alert"""
        try:
            db = SessionLocal()
            audit_log = AuditLog(
                user_id="system",
                action="observability_alert",
                resource_type="observability",
                details={
                    "alert": alert,
                    "severity": alert.get("severity"),
                    "metric": alert.get("metric"),
                    "value": alert.get("value")
                },
                timestamp=datetime.now(timezone.utc)
            )
            db.add(audit_log)
            db.commit()
            db.close()
            
            self.logger.warning(f"Observability alert logged: {alert.get('message')}")
        except Exception as e:
            logger.error(f"Failed to log observability alert: {e}")
    
    async def log_user_action(self, user_id: str, action: str, resource_type: str, resource_id: str = None, details: Dict = None):
        """Log a general user action"""
        try:
            db = SessionLocal()
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                timestamp=datetime.now(timezone.utc)
            )
            db.add(audit_log)
            db.commit()
            db.close()
            
            self.logger.info(f"User action logged: {action} by user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log user action: {e}")
    
    def get_audit_trail(self, user_id: str = None, action: str = None, limit: int = 100) -> list:
        """Get audit trail with optional filters"""
        try:
            db = SessionLocal()
            query = db.query(AuditLog)
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if action:
                query = query.filter(AuditLog.action == action)
            
            audit_logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
            db.close()
            
            return [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "details": log.details,
                    "timestamp": log.timestamp.isoformat()
                }
                for log in audit_logs
            ]
        except Exception as e:
            logger.error(f"Failed to get audit trail: {e}")
            return []

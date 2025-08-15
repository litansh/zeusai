from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.core.database import get_db, SessionLocal
from app.core.mcp_client import MCPClient
from app.core.guardrails import GuardrailEngine
from app.core.audit import AuditLogger
from app.models.infrastructure import Infrastructure, InfrastructureComponent
from app.schemas.infrastructure import (
    InfrastructureCreate,
    InfrastructureUpdate,
    InfrastructureResponse,
    ComponentCreate,
    ComponentResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
mcp_client = MCPClient()
guardrail_engine = GuardrailEngine()
audit_logger = AuditLogger()

@router.post("/", response_model=InfrastructureResponse)
async def create_infrastructure(
    infrastructure: InfrastructureCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create new infrastructure design"""
    try:
        # Validate design through guardrails
        guardrail_result = await guardrail_engine.validate_design(infrastructure.dict())
        if not guardrail_result.allowed:
            raise HTTPException(status_code=400, detail=guardrail_result.reason)
        
        # Create infrastructure record
        db_infrastructure = Infrastructure(
            name=infrastructure.name,
            environment=infrastructure.environment,
            cloud_provider=infrastructure.cloud_provider,
            metadata=infrastructure.metadata,
            created_by=infrastructure.created_by
        )
        db.add(db_infrastructure)
        db.commit()
        db.refresh(db_infrastructure)
        
        # Create components
        for component_data in infrastructure.components:
            db_component = InfrastructureComponent(
                infrastructure_id=db_infrastructure.id,
                name=component_data.name,
                type=component_data.type,
                configuration=component_data.configuration
            )
            db.add(db_component)
        
        db.commit()
        
        # Generate Terraform code in background
        background_tasks.add_task(
            generate_terraform_for_infrastructure,
            db_infrastructure.id,
            infrastructure.dict()
        )
        
        return InfrastructureResponse.from_orm(db_infrastructure)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[InfrastructureResponse])
async def list_infrastructure(
    environment: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all infrastructure"""
    query = db.query(Infrastructure)
    
    if environment:
        query = query.filter(Infrastructure.environment == environment)
    
    if status:
        query = query.filter(Infrastructure.status == status)
    
    infrastructure_list = query.all()
    return [InfrastructureResponse.from_orm(infra) for infra in infrastructure_list]

@router.get("/{infrastructure_id}", response_model=InfrastructureResponse)
async def get_infrastructure(
    infrastructure_id: int,
    db: Session = Depends(get_db)
):
    """Get infrastructure by ID"""
    infrastructure = db.query(Infrastructure).filter(Infrastructure.id == infrastructure_id).first()
    if not infrastructure:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    
    return InfrastructureResponse.from_orm(infrastructure)

@router.put("/{infrastructure_id}", response_model=InfrastructureResponse)
async def update_infrastructure(
    infrastructure_id: int,
    infrastructure_update: InfrastructureUpdate,
    db: Session = Depends(get_db)
):
    """Update infrastructure"""
    db_infrastructure = db.query(Infrastructure).filter(Infrastructure.id == infrastructure_id).first()
    if not db_infrastructure:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    
    # Update fields
    for field, value in infrastructure_update.dict(exclude_unset=True).items():
        setattr(db_infrastructure, field, value)
    
    db.commit()
    db.refresh(db_infrastructure)
    
    return InfrastructureResponse.from_orm(db_infrastructure)

@router.delete("/{infrastructure_id}")
async def delete_infrastructure(
    infrastructure_id: int,
    db: Session = Depends(get_db)
):
    """Delete infrastructure"""
    db_infrastructure = db.query(Infrastructure).filter(Infrastructure.id == infrastructure_id).first()
    if not db_infrastructure:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    
    db.delete(db_infrastructure)
    db.commit()
    
    return {"message": "Infrastructure deleted successfully"}

@router.post("/{infrastructure_id}/deploy")
async def deploy_infrastructure(
    infrastructure_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Deploy infrastructure"""
    db_infrastructure = db.query(Infrastructure).filter(Infrastructure.id == infrastructure_id).first()
    if not db_infrastructure:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    
    if not db_infrastructure.terraform_config:
        raise HTTPException(status_code=400, detail="No Terraform configuration available")
    
    # Update status to deploying
    db_infrastructure.status = "deploying"
    db.commit()
    
    # Deploy in background
    background_tasks.add_task(deploy_infrastructure_task, infrastructure_id)
    
    return {"message": "Infrastructure deployment started"}

@router.get("/state/current")
async def get_current_state():
    """Get current infrastructure state from cloud"""
    try:
        state = await mcp_client.get_infrastructure_state()
        return {"success": True, "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_infrastructure(
    import_request: Dict,
    db: Session = Depends(get_db)
):
    """Import existing infrastructure"""
    try:
        # Use tf-migrator to scan and import
        result = await mcp_client.execute_command("import", import_request)
        
        # Create infrastructure record from imported state
        db_infrastructure = Infrastructure(
            name=import_request.get("name", "Imported Infrastructure"),
            environment=import_request.get("environment", "development"),
            cloud_provider=import_request.get("cloud_provider", "aws"),
            status="active",
            terraform_state=result.get("state"),
            terraform_config=result.get("config")
        )
        db.add(db_infrastructure)
        db.commit()
        db.refresh(db_infrastructure)
        
        return {"success": True, "infrastructure_id": db_infrastructure.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_terraform_for_infrastructure(infrastructure_id: int, design: Dict):
    """Background task to generate Terraform code"""
    try:
        terraform_code = await mcp_client.generate_terraform(design)
        
        # Update infrastructure with Terraform code
        db = SessionLocal()
        db_infrastructure = db.query(Infrastructure).filter(Infrastructure.id == infrastructure_id).first()
        if db_infrastructure:
            db_infrastructure.terraform_config = terraform_code
            db_infrastructure.status = "ready"
            db.commit()
        db.close()
        
    except Exception as e:
        logger.error(f"Failed to generate Terraform for infrastructure {infrastructure_id}: {e}")

async def deploy_infrastructure_task(infrastructure_id: int):
    """Background task to deploy infrastructure"""
    try:
        db = SessionLocal()
        db_infrastructure = db.query(Infrastructure).filter(Infrastructure.id == infrastructure_id).first()
        
        if db_infrastructure and db_infrastructure.terraform_config:
            # Deploy using deploy-mcp
            result = await mcp_client.execute_command("deploy", {
                "terraform_config": db_infrastructure.terraform_config,
                "environment": db_infrastructure.environment
            })
            
            if result.get("success"):
                db_infrastructure.status = "active"
            else:
                db_infrastructure.status = "failed"
            
            db.commit()
        
        db.close()
        
    except Exception as e:
        logger.error(f"Failed to deploy infrastructure {infrastructure_id}: {e}")

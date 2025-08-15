from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from app.core.database import get_db
from app.core.mcp_client import MCPClient

router = APIRouter()
mcp_client = MCPClient()

@router.get("/current")
async def get_current_costs(db: Session = Depends(get_db)):
    """Get current month costs"""
    try:
        result = await mcp_client.execute_command("cost", {})
        return {"success": True, "costs": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage")
async def get_usage_metrics(db: Session = Depends(get_db)):
    """Get usage metrics"""
    try:
        result = await mcp_client.execute_command("usage", {})
        return {"success": True, "usage": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
async def get_cost_forecast(
    months: int = 3,
    db: Session = Depends(get_db)
):
    """Get cost forecast"""
    # Mock forecast data
    forecast = {
        "current_month": 2450.75,
        "forecast": [
            {"month": "2024-02", "estimated": 2600.00},
            {"month": "2024-03", "estimated": 2750.00},
            {"month": "2024-04", "estimated": 2900.00}
        ],
        "trend": "increasing",
        "recommendations": [
            "Consider using reserved instances for predictable workloads",
            "Review and terminate unused EBS volumes",
            "Optimize Lambda function memory allocation"
        ]
    }
    return {"success": True, "forecast": forecast}

@router.get("/breakdown")
async def get_cost_breakdown(
    service: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get cost breakdown by service"""
    breakdown = {
        "ec2": 1200.50,
        "rds": 450.25,
        "s3": 150.00,
        "lambda": 200.00,
        "alb": 100.00,
        "cloudwatch": 50.00,
        "other": 300.00
    }
    
    if service:
        return {"success": True, "cost": breakdown.get(service, 0)}
    
    return {"success": True, "breakdown": breakdown}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.core.database import get_db
from app.core.mcp_client import MCPClient

router = APIRouter()
mcp_client = MCPClient()

@router.get("/metrics")
async def get_metrics(
    query: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get metrics from Prometheus"""
    try:
        result = await mcp_client.query_observability({
            "query": query,
            "start_time": start_time,
            "end_time": end_time
        })
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_alerts(db: Session = Depends(get_db)):
    """Get current alerts"""
    try:
        result = await mcp_client.execute_command("alerts", {})
        return {"success": True, "alerts": result.get("alerts", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_observability(
    query_request: Dict,
    db: Session = Depends(get_db)
):
    """Query observability data"""
    try:
        result = await mcp_client.query_observability(query_request)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

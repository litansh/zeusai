from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from typing import Dict, List, Optional
import redis.asyncio as redis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine, get_db
from app.core.redis_client import get_redis_client
from app.models import Base
from app.api.v1.api import api_router
from app.core.websocket_manager import WebSocketManager
from app.core.mcp_client import MCPClient
from app.core.guardrails import GuardrailEngine
from app.core.audit import AuditLogger

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global WebSocket manager
websocket_manager = WebSocketManager()
mcp_client = MCPClient()
guardrail_engine = GuardrailEngine()
audit_logger = AuditLogger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting ZeusAI Orchestrator...")
    
    # Initialize Redis connection
    app.state.redis = await get_redis_client()
    
    # Initialize MCP clients
    await mcp_client.initialize()
    
    # Initialize guardrails
    await guardrail_engine.initialize()
    
    logger.info("ZeusAI Orchestrator started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ZeusAI Orchestrator...")
    if hasattr(app.state, 'redis'):
        await app.state.redis.close()

app = FastAPI(
    title="ZeusAI Orchestrator",
    description="The ultimate DevOps CoPilot - AI-powered infrastructure orchestration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "ZeusAI Orchestrator",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_client = await get_redis_client()
        await redis_client.ping()
        
        # Check MCP services
        mcp_status = await mcp_client.get_services_status()
        
        return {
            "status": "healthy",
            "redis": "connected",
            "mcp_services": mcp_status,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe":
                await websocket_manager.subscribe(websocket, message.get("channel", "general"))
            elif message.get("type") == "command":
                await handle_command(websocket, message)
            elif message.get("type") == "chat":
                await handle_chat_message(websocket, message)
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket_manager.disconnect(websocket)

async def handle_command(websocket: WebSocket, message: Dict):
    """Handle infrastructure commands via WebSocket"""
    try:
        command = message.get("command")
        params = message.get("params", {})
        
        # Validate command through guardrails
        guardrail_result = await guardrail_engine.validate_command(command, params)
        if not guardrail_result.allowed:
            await websocket.send_text(json.dumps({
                "type": "command_response",
                "success": False,
                "error": guardrail_result.reason,
                "request_id": message.get("request_id")
            }))
            return
        
        # Route command to appropriate MCP service
        result = await mcp_client.execute_command(command, params)
        
        # Log audit trail
        await audit_logger.log_command(
            user_id=message.get("user_id", "unknown"),
            command=command,
            params=params,
            result=result
        )
        
        # Send response
        await websocket.send_text(json.dumps({
            "type": "command_response",
            "success": True,
            "result": result,
            "request_id": message.get("request_id")
        }))
        
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        await websocket.send_text(json.dumps({
            "type": "command_response",
            "success": False,
            "error": str(e),
            "request_id": message.get("request_id")
        }))

async def handle_chat_message(websocket: WebSocket, message: Dict):
    """Handle chat messages for AI assistance"""
    try:
        user_message = message.get("message", "")
        
        # Get context from knowledge base
        context = await mcp_client.get_kb_context(user_message)
        
        # Generate AI response
        response = await mcp_client.generate_ai_response(user_message, context)
        
        await websocket.send_text(json.dumps({
            "type": "chat_response",
            "message": response,
            "context": context,
            "request_id": message.get("request_id")
        }))
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        await websocket.send_text(json.dumps({
            "type": "chat_response",
            "error": str(e),
            "request_id": message.get("request_id")
        }))

@app.post("/api/v1/infrastructure/design")
async def design_infrastructure(
    design_request: Dict,
    db: Session = Depends(get_db)
):
    """Design infrastructure using drag & drop interface"""
    try:
        # Validate design through guardrails
        guardrail_result = await guardrail_engine.validate_design(design_request)
        if not guardrail_result.allowed:
            raise HTTPException(status_code=400, detail=guardrail_result.reason)
        
        # Generate Terraform code
        terraform_code = await mcp_client.generate_terraform(design_request)
        
        # Create Git PR
        pr_url = await mcp_client.create_infrastructure_pr(terraform_code, design_request)
        
        # Log audit trail
        await audit_logger.log_design(
            user_id=design_request.get("user_id", "unknown"),
            design=design_request,
            terraform_code=terraform_code,
            pr_url=pr_url
        )
        
        return {
            "success": True,
            "terraform_code": terraform_code,
            "pr_url": pr_url,
            "message": "Infrastructure design created and PR opened"
        }
        
    except Exception as e:
        logger.error(f"Infrastructure design error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/infrastructure/state")
async def get_infrastructure_state():
    """Get current infrastructure state"""
    try:
        state = await mcp_client.get_infrastructure_state()
        return {
            "success": True,
            "state": state
        }
    except Exception as e:
        logger.error(f"Failed to get infrastructure state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/observability/query")
async def query_observability(query: Dict):
    """Query observability data"""
    try:
        result = await mcp_client.query_observability(query)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Observability query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

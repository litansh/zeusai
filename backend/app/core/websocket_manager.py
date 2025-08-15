import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket
from app.core.redis_client import get_redis_client

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.channel_subscriptions: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all channel subscriptions
        for channel, subscribers in self.channel_subscriptions.items():
            if websocket in subscribers:
                subscribers.remove(websocket)
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def subscribe(self, websocket: WebSocket, channel: str):
        """Subscribe a WebSocket to a channel"""
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()
        
        self.channel_subscriptions[channel].add(websocket)
        logger.info(f"WebSocket subscribed to channel: {channel}")
    
    async def unsubscribe(self, websocket: WebSocket, channel: str):
        """Unsubscribe a WebSocket from a channel"""
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(websocket)
            logger.info(f"WebSocket unsubscribed from channel: {channel}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket client"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            await self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSocket clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def broadcast_to_channel(self, message: str, channel: str):
        """Broadcast a message to all WebSocket clients subscribed to a channel"""
        if channel not in self.channel_subscriptions:
            return
        
        disconnected = []
        for connection in self.channel_subscriptions[channel]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to channel {channel}: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def send_infrastructure_update(self, update: Dict):
        """Send infrastructure update to all clients"""
        message = json.dumps({
            "type": "infrastructure_update",
            "data": update,
            "timestamp": update.get("timestamp")
        })
        await self.broadcast_to_channel(message, "infrastructure")
    
    async def send_observability_alert(self, alert: Dict):
        """Send observability alert to all clients"""
        message = json.dumps({
            "type": "observability_alert",
            "data": alert,
            "timestamp": alert.get("timestamp")
        })
        await self.broadcast_to_channel(message, "alerts")
    
    async def send_deployment_status(self, status: Dict):
        """Send deployment status update to all clients"""
        message = json.dumps({
            "type": "deployment_status",
            "data": status,
            "timestamp": status.get("timestamp")
        })
        await self.broadcast_to_channel(message, "deployments")
    
    async def send_cost_alert(self, alert: Dict):
        """Send cost alert to all clients"""
        message = json.dumps({
            "type": "cost_alert",
            "data": alert,
            "timestamp": alert.get("timestamp")
        })
        await self.broadcast_to_channel(message, "costs")
    
    async def send_guardrail_violation(self, violation: Dict):
        """Send guardrail violation to all clients"""
        message = json.dumps({
            "type": "guardrail_violation",
            "data": violation,
            "timestamp": violation.get("timestamp")
        })
        await self.broadcast_to_channel(message, "guardrails")
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_channel_subscriber_count(self, channel: str) -> int:
        """Get the number of subscribers to a channel"""
        return len(self.channel_subscriptions.get(channel, set()))

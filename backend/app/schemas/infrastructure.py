from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class ComponentCreate(BaseModel):
    name: str
    type: str
    configuration: Dict = {}

class ComponentResponse(BaseModel):
    id: int
    name: str
    type: str
    resource_id: Optional[str] = None
    configuration: Dict = {}
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InfrastructureCreate(BaseModel):
    name: str
    environment: str
    cloud_provider: str = "aws"
    metadata: Dict = {}
    created_by: Optional[int] = None
    components: List[ComponentCreate] = []

class InfrastructureUpdate(BaseModel):
    name: Optional[str] = None
    environment: Optional[str] = None
    cloud_provider: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict] = None

class InfrastructureResponse(BaseModel):
    id: int
    name: str
    environment: str
    cloud_provider: str
    status: str
    terraform_state: Optional[str] = None
    terraform_config: Optional[str] = None
    metadata: Dict = {}
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    components: List[ComponentResponse] = []

    class Config:
        from_attributes = True

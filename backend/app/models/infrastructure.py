from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Infrastructure(Base):
    __tablename__ = "infrastructure"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    environment = Column(String(20), nullable=False)  # dev, staging, prod
    cloud_provider = Column(String(20), default="aws")  # aws, azure, gcp
    status = Column(String(20), default="designing")  # designing, deploying, active, failed
    terraform_state = Column(Text)  # Terraform state JSON
    terraform_config = Column(Text)  # Generated Terraform code
    metadata = Column(JSON)  # Additional metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    components = relationship("InfrastructureComponent", back_populates="infrastructure")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<Infrastructure(id={self.id}, name='{self.name}', environment='{self.environment}')>"

class InfrastructureComponent(Base):
    __tablename__ = "infrastructure_components"
    
    id = Column(Integer, primary_key=True, index=True)
    infrastructure_id = Column(Integer, ForeignKey("infrastructure.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # ec2, vpc, lambda, eks, etc.
    resource_id = Column(String(255))  # Cloud resource ID
    configuration = Column(JSON)  # Component configuration
    status = Column(String(20), default="pending")  # pending, creating, active, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    infrastructure = relationship("Infrastructure", back_populates="components")
    
    def __repr__(self):
        return f"<InfrastructureComponent(id={self.id}, name='{self.name}', type='{self.type}')>"

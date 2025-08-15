import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
import redis.asyncio as redis
from unittest.mock import AsyncMock, patch

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    """Create test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch('app.core.redis_client.get_redis_client') as mock:
        mock_redis = AsyncMock()
        mock.return_value = mock_redis
        yield mock_redis

@pytest.fixture
def mock_mcp_client():
    """Mock MCP client."""
    with patch('app.core.mcp_client.MCPClient') as mock:
        mock_client = AsyncMock()
        mock.return_value = mock_client
        yield mock_client

@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing."""
    from app.models.user import User
    
    user = User(
        username="testadmin",
        email="testadmin@zeusai.com",
        hashed_password="hashed_password",
        full_name="Test Admin",
        role="admin",
        is_superuser=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_infrastructure(db_session, admin_user):
    """Create sample infrastructure for testing."""
    from app.models.infrastructure import Infrastructure, InfrastructureComponent
    
    infra = Infrastructure(
        name="test-infrastructure",
        environment="development",
        cloud_provider="aws",
        status="active",
        created_by=admin_user.id
    )
    db_session.add(infra)
    db_session.commit()
    db_session.refresh(infra)
    
    component = InfrastructureComponent(
        infrastructure_id=infra.id,
        name="test-ec2",
        type="ec2",
        configuration={"instance_type": "t3.micro"},
        status="active"
    )
    db_session.add(component)
    db_session.commit()
    
    return infra

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from .config import settings
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

# Import Base from models.base
from .models.base import Base

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency to get database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Drop tables
async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class MongoDBClient:
    _instance = None
    _client = None
    
    def __new__(cls, uri="mongodb://localhost:27017"):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            cls._client = AsyncIOMotorClient(uri)
        return cls._instance
    
    def get_collection(self, db_name="conversations_db", collection_name="conversations"):
        return self._client[db_name][collection_name]
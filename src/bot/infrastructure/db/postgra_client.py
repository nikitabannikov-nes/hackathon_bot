from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DB_URL")

class SessionWithDB:
    def __init__(self):
        self.name = "sessin"

    async def commit(self):
        if self.session and self._session.is_active:
            await self.session.commit()

    async def rollback(self):
        if self.session and self.session.is_active:
            await self.session.rollback()
    
    async def __aenter__(self):
        engine = create_async_engine(DATABASE_URL)
        self.session = async_sessionmaker(autoflush=False, bind=engine, class_=AsyncSession)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.commit()
        finally:
            if self.session:
                await self.session.close()

postgra_session = SessionWithDB()                






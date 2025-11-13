from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    fathername = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False) 
    tg_id = Column(String(100), nullable=False, unique=True)
    username = Column(String(100), nullable=False)
    area = Column(String(100), nullable=True)
    team = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
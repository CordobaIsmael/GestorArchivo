from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    whatsapp_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    
    # Preferencias configurables del usuario (Etapa 5/6 avanzada)
    currency = Column(String, default="ARS", nullable=False)  # ej: "ARS", "USD", "EUR"
    language = Column(String, default="es", nullable=False)   # ej: "es", "en"
    timezone = Column(String, default="America/Argentina/Buenos_Aires", nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("ConversationLog", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("UserMemory", back_populates="user", cascade="all, delete-orphan")

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True) # null para categorías por defecto
    name = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)  # "Gasto", "Ingreso", "Ambos"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    transactions = relationship("Transaction", back_populates="category")

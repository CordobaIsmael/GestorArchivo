from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # "Gasto", "Ingreso"
    description = Column(String, nullable=True)
    date = Column(Date, nullable=False, server_default=func.current_date())
    
    raw_message = Column(String, nullable=True)  # Mensaje de texto original
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    direction = Column(String, nullable=False)  # "incoming" (del usuario) o "outgoing" (del bot)
    message = Column(String, nullable=False)    # Contenido del texto
    
    # Datos de auditoría técnica (Etapa 4/5 avanzada)
    ai_called = Column(Boolean, default=False)
    intent_detected = Column(String, nullable=True) # ej: "GET_BALANCE", "ADD_EXPENSE"
    tools_called = Column(String, nullable=True)     # JSON string con detalles de herramientas ejecutadas
    latency_ms = Column(Integer, nullable=True)      # Tiempo de procesamiento en ms
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user = relationship("User", back_populates="logs")

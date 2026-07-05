import time
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app import models
from app.schemas.intent import Intent
from app.engines.router import CommandRouter
from app.engines.orchestrator import AIOrchestrator

# Importar las herramientas
from app.tools.tool_get_balance import GetBalanceTool
from app.tools.tool_get_history import GetHistoryTool
from app.tools.tool_add_transaction import AddTransactionTool
from app.tools.tool_confirm_transaction import ConfirmTransactionTool

router = APIRouter()

# --- MAPA DE INTENCIONES A HERRAMIENTAS ---
TOOLS_MAP = {
    "GET_BALANCE": GetBalanceTool(),
    "GET_HISTORY": GetHistoryTool(),
    "ADD_EXPENSE": AddTransactionTool(),
    "ADD_INCOME": AddTransactionTool(),
    "CONFIRM_TRANSACTION": ConfirmTransactionTool(),
}

# --- ESQUEMAS DE ENTRADA Y SALIDA ---
from pydantic import BaseModel, Field

class MessageRequest(BaseModel):
    user: str = Field(..., example="5491112345678@s.whatsapp.net", description="whatsapp_id del remitente")
    message: str = Field(..., example="Gasté 1500 en pizza.", description="Mensaje en lenguaje natural")

class MessageResponse(BaseModel):
    response: str = Field(..., example="Mensaje procesado")

# Instancia global del orquestador de IA
orchestrator = AIOrchestrator()


@router.post("/message", response_model=MessageResponse, status_code=status.HTTP_200_OK, tags=["Chat"])
def process_message(msg_in: MessageRequest, db: Session = Depends(get_db)):
    """
    Procesa un mensaje entrante (de WhatsApp o chat de n8n) utilizando el Command Router
    y OpenAI como fallback. Registra auditoría completa.
    """
    start_time = time.time()
    whatsapp_id = msg_in.user
    message_text = msg_in.message

    # 1. OBTENER O CREAR USUARIO EN BD
    db_user = db.query(models.User).filter_by(whatsapp_id=whatsapp_id).first()
    if not db_user:
        db_user = models.User(whatsapp_id=whatsapp_id, name="Usuario WhatsApp")
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    # 2. AUDITAR MENSAJE ENTRANTE (conversation_logs)
    incoming_log = models.ConversationLog(
        user_id=db_user.id,
        direction="incoming",
        message=message_text,
        ai_called=False
    )
    db.add(incoming_log)
    db.commit()

    # 3. EJECUTAR COMMAND ROUTER (REGEX)
    ai_called = False
    intent = CommandRouter.route(message_text, db, db_user)

    # 4. FALLBACK A IA (OPENAI) SI REGEX NO COINCIDIÓ
    if intent is None:
        ai_called = True
        intent = orchestrator.classify_intent(message_text)

    # 5. EJECUTAR LA HERRAMIENTA ASOCIADA A LA INTENCIÓN
    response_text = ""
    if intent.name in TOOLS_MAP:
        tool = TOOLS_MAP[intent.name]
        response_text = tool.execute(intent, db, db_user)
    elif intent.name == "UNKNOWN":
        # Manejar caso de error de OpenAI
        error_msg = intent.parameters.get("error")
        if error_msg:
            response_text = f"⚠️ *Error de IA:* {error_msg}"
        else:
            response_text = (
                "🤖 *No entendí tu solicitud.*\n\n"
                "Prueba con comandos como:\n"
                "*   `saldo` o `cuánto tengo`\n"
                "*   `historial` o `mis movimientos`\n"
                "*   `Gasté 1500 en pizza` (para registrar gastos)\n"
                "*   `Cobré 30000 de sueldo` (para registrar ingresos)"
            )
    else:
        response_text = f"⚠️ Intención clasificada como '{intent.name}' pero no tiene una herramienta asociada."

    latency_ms = int((time.time() - start_time) * 1000)

    # 6. AUDITAR RESPUESTA SALIENTE (conversation_logs)
    outgoing_log = models.ConversationLog(
        user_id=db_user.id,
        direction="outgoing",
        message=response_text,
        ai_called=ai_called,
        intent_detected=intent.name,
        tools_called=json.dumps({
            "intent_source": intent.source,
            "confidence": intent.confidence,
            "parameters": intent.parameters
        }),
        latency_ms=latency_ms
    )
    db.add(outgoing_log)
    db.commit()

    return MessageResponse(response=response_text)

import re
from sqlalchemy.orm import Session
from app.schemas.intent import Intent
from app.models.user import User
from app.models.memory import UserMemory

# Mapa de comandos predefinidos por Expresiones Regulares
REGEX_COMMANDS = [
    {
        "intent": "GET_BALANCE",
        "patterns": [
            r"^/saldo$",
            r"^\s*saldo\s*$",
            r".*saldo.*",
            r"cu[aá]nto.*tengo",
            r"^balance$"
        ]
    },
    {
        "intent": "GET_HISTORY",
        "patterns": [
            r"^\s*historial\s*$",
            r".*historial.*",
            r".*movimientos.*",
            r"^\s*gastos\s*$"
        ]
    }
]

class CommandRouter:
    @staticmethod
    def route(message_text: str, db: Session, user: User) -> Intent | None:
        text_clean = message_text.strip().lower()

        # 1. INTERCEPTAR CONFIRMACIÓN: si hay una transacción pendiente de confirmar
        pending_tx = db.query(UserMemory).filter_by(user_id=user.id, key="pending_transaction").first()
        if pending_tx:
            # Patrones de confirmación (Sí / No)
            yes_patterns = [r"^(s[ií]|confirm[oó]|ok|dale|correcto|s|si)$"]
            no_patterns = [r"^(no|cancel[ao]|incorrecto|n)$"]

            for pat in yes_patterns:
                if re.match(pat, text_clean):
                    return Intent(
                        name="CONFIRM_TRANSACTION",
                        confidence=1.0,
                        source="regex",
                        parameters={"answer": "yes"}
                    )
            
            for pat in no_patterns:
                if re.match(pat, text_clean):
                    return Intent(
                        name="CONFIRM_TRANSACTION",
                        confidence=1.0,
                        source="regex",
                        parameters={"answer": "no"}
                    )

        # 2. VERIFICACIÓN DE COMANDOS REGEX ESTÁNDAR
        for cmd in REGEX_COMMANDS:
            for pattern in cmd["patterns"]:
                if re.search(pattern, text_clean):
                    return Intent(
                        name=cmd["intent"],
                        confidence=1.0,
                        source="regex",
                        parameters={}
                    )
        
        # Si no coincide con ningún patrón local, devolver None (indica fallback a OpenAI)
        return None

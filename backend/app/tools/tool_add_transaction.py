import json
from sqlalchemy.orm import Session
from app.tools.base import BaseTool
from app.schemas.intent import Intent
from app.models.user import User
from app.models.memory import UserMemory

class AddTransactionTool(BaseTool):
    def execute(self, intent: Intent, db: Session, user: User) -> str:
        params = intent.parameters
        amount = params.get("amount")
        tx_type = "Gasto" if intent.name == "ADD_EXPENSE" else "Ingreso"

        if amount is None or amount <= 0:
            action_verb = "gastaste" if tx_type == "Gasto" else "recibiste"
            return f"❌ No pude identificar un monto válido. ¿Podrías indicarme cuánto {action_verb}?"

        description = params.get("description", "Varios")
        category_name = params.get("category_name")
        
        # Categoría por defecto si no viene especificada
        if not category_name:
            category_name = "Otros Gastos" if tx_type == "Gasto" else "Otros Ingresos"

        raw_message = params.get("raw_message", "")

        # Estructurar la transacción pendiente
        pending_tx = {
            "amount": amount,
            "type": tx_type,
            "description": description,
            "category_name": category_name,
            "raw_message": raw_message
        }

        # Guardar en memoria de usuario (sobreescribiendo si ya existe una pendiente)
        db_memory = db.query(UserMemory).filter_by(user_id=user.id, key="pending_transaction").first()
        if not db_memory:
            db_memory = UserMemory(user_id=user.id, key="pending_transaction")
            db.add(db_memory)

        db_memory.value = json.dumps(pending_tx)
        db.commit()

        symbol = "$" if user.currency in ["ARS", "USD", "COP", "MXN"] else user.currency
        type_str = "Gasto 🔴" if tx_type == "Gasto" else "Ingreso 🟢"
        
        return (
            f"¿Confirmas que deseas registrar este movimiento?\n\n"
            f"*   **Tipo:** {type_str}\n"
            f"*   **Monto:** {symbol}{amount:,.2f}\n"
            f"*   **Categoría:** {category_name}\n"
            f"*   **Detalle:** {description}\n\n"
            f"*(Responde 'Sí' para guardar o 'No' para cancelar)*"
        )

import json
from sqlalchemy.orm import Session
from app.tools.base import BaseTool
from app.schemas.intent import Intent
from app.models.user import User
from app.models.memory import UserMemory
from app.models.transaction import Transaction
from app.models.category import Category

class ConfirmTransactionTool(BaseTool):
    def execute(self, intent: Intent, db: Session, user: User) -> str:
        # Recuperar la transacción pendiente
        db_memory = db.query(UserMemory).filter_by(user_id=user.id, key="pending_transaction").first()
        if not db_memory:
            return "No tienes ninguna transacción pendiente de confirmar. Di por ejemplo: *'Gasté 1500 en pizza'* para iniciar."

        answer = intent.parameters.get("answer", "no")

        if answer == "no":
            # Eliminar la transacción pendiente
            db.delete(db_memory)
            db.commit()
            return "❌ Registro cancelado. Los datos no se guardaron."

        # Si responde que sí, guardar en la base de datos
        try:
            pending_tx = json.loads(db_memory.value)
            amount = pending_tx["amount"]
            tx_type = pending_tx["type"]
            description = pending_tx["description"]
            category_name = pending_tx["category_name"]
            raw_message = pending_tx["raw_message"]

            # Buscar categoría en la base de datos (por usuario o global)
            category = db.query(Category).filter(
                Category.name == category_name,
                (Category.user_id == user.id) | (Category.user_id == None)
            ).first()

            category_id = category.id if category else None

            # Crear y guardar la transacción
            tx = Transaction(
                user_id=user.id,
                category_id=category_id,
                amount=amount,
                type=tx_type,
                description=description,
                raw_message=raw_message
            )
            db.add(tx)
            
            # Borrar de la memoria
            db.delete(db_memory)
            db.commit()

            symbol = "$" if user.currency in ["ARS", "USD", "COP", "MXN"] else user.currency
            type_str = "Gasto 🔴" if tx_type == "Gasto" else "Ingreso 🟢"
            
            return (
                f"✅ **¡Movimiento guardado con éxito!**\n\n"
                f"*   **Tipo:** {type_str}\n"
                f"*   **Monto:** {symbol}{amount:,.2f}\n"
                f"*   **Categoría:** {category_name}\n"
                f"*   **Detalle:** {description}"
            )

        except Exception as e:
            db.rollback()
            return f"❌ Ocurrió un error al procesar tu confirmación: {str(e)}"

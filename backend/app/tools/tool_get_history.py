from sqlalchemy.orm import Session
from app.tools.base import BaseTool
from app.schemas.intent import Intent
from app.models.user import User
from app.models.transaction import Transaction

class GetHistoryTool(BaseTool):
    def execute(self, intent: Intent, db: Session, user: User) -> str:
        limit = intent.parameters.get("limit", 10)
        
        txs = db.query(Transaction).filter(
            Transaction.user_id == user.id
        ).order_by(
            Transaction.date.desc(),
            Transaction.created_at.desc()
        ).limit(limit).all()

        if not txs:
            return "📋 **Historial vacío:** Aún no has registrado ningún movimiento. Prueba diciendo por ejemplo: *'Gasté 1500 en almuerzo'*."

        symbol = "$" if user.currency in ["ARS", "USD", "COP", "MXN"] else user.currency
        text = "📋 **Tus movimientos recientes:**\n\n"
        
        for tx in txs:
            emoji = "🔴" if tx.type == "Gasto" else "🟢"
            sign = "-" if tx.type == "Gasto" else "+"
            cat_name = tx.category.name if tx.category else "Sin categoría"
            desc = f" -> {tx.description}" if tx.description else ""
            
            text += f"{emoji} {tx.date}: {sign}{symbol}{tx.amount:,.2f} [{cat_name}]{desc}\n"

        return text

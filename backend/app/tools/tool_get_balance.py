from sqlalchemy.orm import Session
from sqlalchemy import func
from app.tools.base import BaseTool
from app.schemas.intent import Intent
from app.models.user import User
from app.models.transaction import Transaction

class GetBalanceTool(BaseTool):
    def execute(self, intent: Intent, db: Session, user: User) -> str:
        # Sumar ingresos
        incomes = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == "Ingreso"
        ).scalar() or 0.0

        # Sumar gastos
        expenses = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == "Gasto"
        ).scalar() or 0.0

        balance = incomes - expenses
        
        # Formatear moneda según preferencia del usuario
        symbol = "$" if user.currency in ["ARS", "USD", "COP", "MXN"] else user.currency
        return f"💰 **Tu balance actual:** {symbol}{balance:,.2f}"

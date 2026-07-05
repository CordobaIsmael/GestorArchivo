from sqlalchemy.orm import Session
from app.schemas.intent import Intent
from app.models.user import User

class BaseTool:
    def execute(self, intent: Intent, db: Session, user: User) -> str:
        """
        Ejecuta la herramienta correspondiente para procesar la intención.
        Retorna la respuesta en texto que será enviada al usuario.
        """
        raise NotImplementedError("Las herramientas deben implementar el método execute")

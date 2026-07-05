from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import Session
from typing import Generator
from app.core.config import settings

# Crear el motor de SQLAlchemy utilizando settings.db_url
engine = create_engine(
    settings.db_url,
    pool_pre_ping=True,  # Verifica que la conexión siga activa antes de enviar comandos
)

# Creador de sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para la declaración de modelos
Base = declarative_base()

# Dependencia de FastAPI para obtener la sesión de base de datos en los endpoints
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

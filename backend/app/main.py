from fastapi import FastAPI
from app.database.connection import engine, Base, get_db
from app.api.v1.api import api_router
from app import models  # Asegura que todos los modelos estén importados en Base

# Crear tablas en el arranque de la aplicación
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Orquestador Financiero Inteligente API",
    description="Backend principal en arquitectura simplificada con Command Router",
    version="1.1.0"
)

# --- SEMILLA DE CATEGORÍAS GLOBALES ---
DEFAULT_CATEGORIES = [
    {"name": "Alimentos", "type": "Gasto"},
    {"name": "Transporte", "type": "Gasto"},
    {"name": "Vivienda", "type": "Gasto"},
    {"name": "Entretenimiento", "type": "Gasto"},
    {"name": "Salud", "type": "Gasto"},
    {"name": "Sueldo", "type": "Ingreso"},
    {"name": "Inversiones", "type": "Ingreso"},
    {"name": "Ventas", "type": "Ingreso"},
    {"name": "Otros Gastos", "type": "Gasto"},
    {"name": "Otros Ingresos", "type": "Ingreso"},
]

@app.on_event("startup")
def seed_categories():
    db = next(get_db())
    try:
        for cat_data in DEFAULT_CATEGORIES:
            existing = db.query(models.Category).filter_by(
                name=cat_data["name"], 
                user_id=None
            ).first()
            if not existing:
                cat = models.Category(name=cat_data["name"], type=cat_data["type"], user_id=None)
                db.add(cat)
        db.commit()
    except Exception as e:
        print(f"Error al sembrar categorías por defecto: {e}")
        db.rollback()
    finally:
        db.close()

# --- RUTAS PRINCIPALES ---

@app.get("/health", tags=["Health"])
def health_check():
    """
    Verifica el estado del backend orquestador.
    """
    return {
        "status": "ok",
        "service": "financial-ai-backend"
    }

# Registrar el router de la v1
app.include_router(api_router, prefix="/api/v1")

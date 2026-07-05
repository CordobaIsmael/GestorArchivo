from fastapi import APIRouter
from .endpoints import message

api_router = APIRouter()

# Registrar todos los sub-routers de la v1 de la API
api_router.include_router(message.router, prefix="")

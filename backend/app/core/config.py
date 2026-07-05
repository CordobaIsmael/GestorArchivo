from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

class Settings(BaseSettings):
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="control_finanzas", alias="POSTGRES_DB")
    postgres_port: int = Field(default=5435, alias="POSTGRES_PORT")
    
    # URL de conexión para desarrollo local fuera de Docker (usa el puerto mapeado 5435)
    database_url: str = Field(default="postgresql://postgres:finanzas_secure_pwd_2026@127.0.0.1:5435/control_finanzas", alias="DATABASE_URL_LOCAL")
    
    # URL de conexión dentro de Docker (inyectado por docker-compose)
    database_url_docker: str | None = Field(default=None, alias="DATABASE_URL")
    
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    @property
    def db_url(self) -> str:
        # Priorizar la URL de Docker si estamos dentro de la red del contenedor
        if os.environ.get("RUNNING_IN_DOCKER") == "true" and self.database_url_docker:
            return self.database_url_docker
        return self.database_url

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Buscar el archivo .env también en directorios superiores si no está en la carpeta de ejecución
# (esto es útil para uvicorn corriendo desde dentro de backend/)
if not os.path.exists(".env") and os.path.exists("../.env"):
    settings = Settings(_env_file="../.env")
elif not os.path.exists(".env") and os.path.exists("../../.env"):
    settings = Settings(_env_file="../../.env")
else:
    settings = Settings()

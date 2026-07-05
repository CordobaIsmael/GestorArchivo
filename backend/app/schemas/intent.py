from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class Intent(BaseModel):
    name: str = Field(..., example="GET_BALANCE", description="Nombre de la intención clasificada")
    confidence: float = Field(..., example=1.0, description="Nivel de confianza (0.0 a 1.0)")
    source: str = Field(..., example="regex", description="Origen de la clasificación ('regex' o 'openai')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parámetros extraídos de la intención")

import json
from openai import OpenAI
from app.core.config import settings
from app.schemas.intent import Intent

class AIOrchestrator:
    def __init__(self):
        # Inicializa el cliente oficial de OpenAI usando la api key configurada en .env
        self.client = OpenAI(api_key=settings.openai_api_key)

    def classify_intent(self, message_text: str) -> Intent:
        # Si no hay API Key configurada (caso de que el pago esté demorado o falte configurar),
        # devolvemos UNKNOWN para evitar colapsar la ejecución de FastAPI.
        if not settings.openai_api_key or settings.openai_api_key == "tu_openai_api_key_aqui":
            return Intent(
                name="UNKNOWN",
                confidence=1.0,
                source="openai",
                parameters={"error": "OpenAI API Key no configurada en el servidor backend."}
            )

        system_prompt = (
            "Eres el clasificador de intenciones del Agente Financiero Inteligente. Tu tarea es analizar el mensaje del usuario y clasificarlo.\n\n"
            "Debes retornar UNICAMENTE un objeto JSON con el siguiente esquema:\n"
            "{\n"
            '  "intent": "ADD_EXPENSE" | "ADD_INCOME" | "UNKNOWN",\n'
            '  "confidence": float,\n'
            '  "parameters": {\n'
            '    "amount": float | null,\n'
            '    "description": string | null,\n'
            '    "category_name": string | null,\n'
            '    "raw_message": string\n'
            "  }\n"
            "}\n\n"
            "REGLAS:\n"
            "1. Si el usuario reporta un gasto, pago, compra o salida de dinero, la intención es 'ADD_EXPENSE'.\n"
            "2. Si el usuario reporta un cobro, sueldo, venta, premio o entrada de dinero, la intención es 'ADD_INCOME'.\n"
            "3. En 'parameters', extrae el monto numérico en 'amount' (como float), una breve descripción en 'description' (ej. 'pizza', 'sueldo', 'nafta') y la categoría en 'category_name'.\n"
            "4. Sugiere una categoría apropiada únicamente de esta lista predefinida:\n"
            "   [Alimentos, Transporte, Vivienda, Entretenimiento, Salud, Sueldo, Inversiones, Ventas, Otros Gastos, Otros Ingresos]\n"
            "5. Si el mensaje no tiene que ver con finanzas personales (registro, saldos, movimientos, etc.), la intención es 'UNKNOWN'.\n"
            "6. 'raw_message' debe contener exactamente el mensaje enviado por el usuario."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message_text}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )

            result_str = response.choices[0].message.content
            data = json.loads(result_str)

            return Intent(
                name=data.get("intent", "UNKNOWN"),
                confidence=data.get("confidence", 0.9),
                source="openai",
                parameters=data.get("parameters", {})
            )

        except Exception as e:
            # En caso de error de conexión o API, fallback a UNKNOWN de forma segura
            return Intent(
                name="UNKNOWN",
                confidence=0.0,
                source="openai",
                parameters={"error": str(e)}
            )

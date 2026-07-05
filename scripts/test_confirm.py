import json
import urllib.request
from sqlalchemy import create_engine, text

# Conectamos a la BD mapeada localmente en el puerto 5435
DB_URL = "postgresql://postgres:finanzas_secure_pwd_2026@127.0.0.1:5435/control_finanzas"
engine = create_engine(DB_URL)

def run_test():
    print("--- 1. Insertando transacción pendiente simulada en user_memory ---")
    pending_tx = {
        "amount": 15000.0,
        "type": "Gasto",
        "description": "pizza de prueba",
        "category_name": "Alimentos",
        "raw_message": "Gasté 15000 en pizza"
    }
    
    with engine.connect() as conn:
        # Obtener el ID del usuario
        user_id = conn.execute(text("SELECT id FROM users WHERE whatsapp_id = 'chat-usuario-local'")).scalar()
        if not user_id:
            print("El usuario 'chat-usuario-local' no existe. Iniciando una llamada al backend para crearlo...")
            # Llamar al backend una vez para registrar al usuario
            req = urllib.request.Request(
                "http://127.0.0.1:8000/api/v1/message",
                data=json.dumps({"user": "chat-usuario-local", "message": "saldo"}).encode(),
                headers={"Content-Type": "application/json"}
            )
            urllib.request.urlopen(req).read()
            user_id = conn.execute(text("SELECT id FROM users WHERE whatsapp_id = 'chat-usuario-local'")).scalar()

        # Limpiar cualquier residuo previo
        conn.execute(text("DELETE FROM user_memory WHERE user_id = :uid AND key = 'pending_transaction'"), {"uid": user_id})
        conn.execute(text("DELETE FROM transactions WHERE user_id = :uid"), {"uid": user_id})
        
        # Insertar la transacción pendiente
        conn.execute(
            text("INSERT INTO user_memory (user_id, key, value) VALUES (:uid, 'pending_transaction', :val)"),
            {"uid": user_id, "val": json.dumps(pending_tx)}
        )
        conn.commit()
        print(f"Transacción pendiente insertada para el usuario ID: {user_id}")

    print("\n--- 2. Enviando confirmación 'sí' al backend ---")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/message",
        data=json.dumps({"user": "chat-usuario-local", "message": "sí"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        res = urllib.request.urlopen(req).read()
        res_json = json.loads(res.decode("utf-8"))
        print("Respuesta del Backend:")
        # ascii() escapa emojis como unicode strings, 100% seguro en cualquier codificación de terminal
        print(ascii(res_json["response"]))
    except Exception as e:
        print(f"Error al enviar confirmacion: {e}")
        return

    print("\n--- 3. Verificando base de datos ---")
    with engine.connect() as conn:
        # Verificar si la transacción fue creada en la tabla 'transactions'
        txs = conn.execute(text("SELECT t.amount, t.type, t.description, c.name FROM transactions t LEFT JOIN categories c ON t.category_id = c.id")).all()
        print(f"Transacciones en DB (Esperado: 1): {len(txs)}")
        for tx in txs:
            print(f"- Gasto registrado: {tx[0]} en {tx[3]} por '{tx[2]}'")

        # Verificar si se eliminó de user_memory
        memory_count = conn.execute(text("SELECT count(*) FROM user_memory WHERE key = 'pending_transaction'")).scalar()
        print(f"Registros pendientes en memoria (Esperado: 0): {memory_count}")

if __name__ == "__main__":
    run_test()

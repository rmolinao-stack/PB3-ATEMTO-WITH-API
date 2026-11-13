from typing import Any


def ensure_schema() -> None:
    """Crea las tablas si no existen (se llama al arrancar FastAPI)."""
    # TBD
    # CREATE TABLE según Conversation / Message (si ya están, no hace nada)
    # SQLModel.metadata.create_all(engine)

def save_turn(thread_id: str, pregunta: str, respuesta: str) -> None:
    """Guarda un turno completo: mensaje user + mensaje assistant."""
    #TBD

def list_messages(thread_id: str) -> list[dict[str, Any]]:
    """Lista mensajes del hilo ordenados por id (para GET …/messages)."""
    #TBD 

def storage_mode() -> str:
    """Devuelve el modo de almacenamiento actual."""
    #TBD

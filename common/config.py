""" En este fichero se definen los parametros de configuración globales de todo el proyecto."""

from pathlib import Path
import os

# --- Ingesta y chunking ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150 # Aplicamos un 15% del tamaño del chunk.

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
CHUNKS_JSON = OUTPUT_DIR / "chunks.json"
EMBEDDINGS_JSON = OUTPUT_DIR / "embeddings.json"

EMBEDDING_MODEL = "gemini-embedding-2"
MAX_CHUNKS_EMBED: int | None = None  # None = embeddear todos los chunks
EMBED_BATCH_SIZE = 50 # Para enviar lotes de información en paquetes a la API de embeddings y no saturarla.
EMBEDDING_SLEEP = 60 # Segundos de espera entre lotes de embeddings para no saturar la API.

EXTENSIONES_TEXTO = {".txt", ".md"}
EXTENSIONES_PDF = {".pdf"}
EXTENSIONES_CSV = {".csv"}

# --- Indexación Chroma ---
CHROMA_DIR = OUTPUT_DIR / "chroma_db"
COLLECTION_NAME = "tarifas_atm_bcn"
INDEX_BATCH_SIZE = 100

# --- Retrieval---
TOP_K = 5 # Número de resultados a recuperar en la búsqueda (retrieval)

# --- Generación ---
#GEMINI_MODEL = "gemini-3.1-flash-lite"
#GEMINI_MODEL = "gemini-3-flash-preview"
#GEMINI_MODEL = "gemini-3.1-flash-lite-preview"
GEMINI_MODEL = "gemini-3.5-flash-lite"
#GEMINI_MODEL = "gemini-3.6-flash"

GENERATION_TEMPERATURE = 0.2
AGENT_TEMPERATURE = 0.2

# --- Evaluación ---
QUERIES_EVAL_JSON = Path(__file__).parent.parent / "queries" / "preguntas_eval.json"

# --- Parámetros por defecto para el multi agente ---
MAX_STEPS_DEFAULT = 4
MAX_TURNS_DEFAULT = 6
MAX_ITER = 8

DEMO_MENSAJES = [
    (
        "Como puedo ir de Santa Coloma a Alella, que abono tengo que comprar si realizar más de 10 viajes al mes y a que hora llega el próximo metro a Santa Coloma."
    ),
    #(
    #    "Dime la ruta que hay entre creu alta y ripoll. Dime los transbordos necesarios. Qu billete tengo que comprar para hacer este viaje. Y cuando llegaría el siguiente tren si mi estación origen es creu alta."
    #),
]

PLANO_ATM_PATH = Path(__file__).parent.parent / "assets" / "plano_ATM.jpg"
ESTACIONS_CSV_PATH = Path(__file__).parent.parent / "assets"  / "estacions.csv"

TMB_METRO_ESTACIONS_URL = "https://api.tmb.cat/v1/itransit/metro/estacions?estacions="
HTTP_TIMEOUT_SECONDS = 12

# --- Parámetros para la API ---

API_KEY: str | None = os.getenv("API_KEY") or None
RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))

# Tope de tiempo por turno (POST /ask y /approve).
# Miramos si está definida en el docker o similar y sino lo marcamos a 300 segundos (5 minutos) por defecto.
ASK_TIMEOUT_SECONDS: int = int(os.getenv("ASK_TIMEOUT_SECONDS", "300"))

_cors_raw = os.getenv(
    "CORS_ORIGINS",
    "http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:8501,http://localhost:3000",
)
CORS_ORIGINS: list[str] = [o.strip() for o in _cors_raw.split(",") if o.strip()]

CORS_ALLOW_CREDENTIALS: bool = os.getenv(
    "CORS_ALLOW_CREDENTIALS", "false"
).lower() in ("true", "1", "yes")

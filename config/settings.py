"""Configuración central del proyecto."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "techstore.db"
CHROMA_DIR = DATA_DIR / "chroma_db"

# Reglas de negocio (umbrales centralizados: un cambio aquí afecta a todo el
# proyecto, sin buscar "números mágicos" en el código).
DIAS_PLAZO = 30
UMBRAL_APROBACION = 100_000
UMBRAL_PREFERENTE = 50_000
UMBRAL_FRAUDE = 3

# LLM
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")

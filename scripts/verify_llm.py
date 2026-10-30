"""Paso: Verifica que Gemini responde desde tu entorno.

Uso:
    python scripts/verify_llm.py

Salida esperada:
    Hola desde Gemini
"""

import os
import time

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Carga las variables del archivo .env al entorno del proceso
load_dotenv()

# El nombre del modelo vive en LLM_MODEL para poder cambiarlo sin tocar código
modelo = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")

# timeout=30     -> cada intento corta a los 30 s en vez de colgarse
# max_retries=0  -> desactiva el backoff silencioso del SDK (esa era la
#                    causa de que el script "no hiciera nada" ante un 503)
llm = ChatGoogleGenerativeAI(model=modelo, timeout=30, max_retries=0)

INTENTOS = 3
ESPERA_ENTRE_INTENTOS = 5

for intento in range(1, INTENTOS + 1):
    print(f"[{intento}/{INTENTOS}] Consultando {modelo}...", flush=True)
    try:
        respuesta = llm.invoke("Responde solo: 'Hola desde Gemini'")
        print(respuesta.content)
        break
    except Exception as exc:  # Motivo exacto en pantalla
        print(f"  -> {type(exc).__name__}: {str(exc)[:200]}", flush=True)
        if intento == INTENTOS:
            print("FALLO: Gemini no respondio tras3 intentos.", flush=True)
            raise SystemExit(1) from exc
        time.sleep(ESPERA_ENTRE_INTENTOS)

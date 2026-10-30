# Referencia de cuotas — Modelos Gemini

> Fuente: tabla compartida por el estudiante desde AI Studio (oct 2026).
> **Formato de las columnas: `usado / límite`.** Los valores "0 / X" significan
> que aún no se ha usado nada de ese límite en la ventana vigente.

## Definiciones

| Sigla | Significado | Se reinicia |
|---|---|---|
| RPM | Requests por minuto | cada minuto |
| TPM | Tokens por minuto | cada minuto |
| RPD | Requests por día | cada día (medianoche PT) |

## Tabla de cuotas

| Modelo | Categoría | RPM | TPM | RPD |
|---|---|---|---|---|
| Gemini 3.5 Flash Lite | Texto de salida | 1 / 15 | 5 / 250K | 1 / 500 |
| Gemini 2.5 Flash | Texto de salida | 0 / 5 | 0 / 250K | 0 / 20 |
| Gemini 2.5 Flash Lite | Texto de salida | 0 / 10 | 0 / 250K | 0 / 20 |
| Gemini 3 Flash | Texto de salida | 0 / 5 | 0 / 250K | 0 / 20 |
| Gemini 3.1 Flash Lite | Texto de salida | 0 / 15 | 0 / 250K | 0 / 500 |
| Gemini 3.6 Flash | Texto de salida | 0 / 5 | 0 / 250K | 0 / 20 |
| Gemini Embedding 1 | Otros | 0 / 100 | 0 / 30K | 0 / 1K |
| Gemini Embedding 2 | Otros | 0 / 100 | 0 / 30K | 0 / 1K |
| Gemma 4 26B | Otros | 0 / 30 | 0 / 16K | 0 / 14.4K |
| Gemma 4 31B | Otros | 0 / 30 | 0 / 16K | 0 / 14.4K |

## Modelo oficial del proyecto

- **`LLM_MODEL=gemini-3.8-flash`** (exigido por la guía de la fase).
- Estado (30 oct 2026): el modelo **existe** en la cuenta pero devuelve
  `429 RESOURCE_EXHAUSTED` (cuota diaria agotada) y `503` intermitentes.
- **No aparece en la tabla de arriba** → revisar su cuota en AI Studio cuando
  se renueve y usarlo como modelo final de demo.

## Estrategia de uso por fase

| Fase | Modelo sugerido | Motivo |
|---|---|---|
| 0 (verificación) | `gemini-3.5-flash-lite` | 500 RPD, suficiente para validar |
| 2–7 (desarrollo) | `gemini-3.5-flash-lite` | Mucho margen; cambiar solo en `.env` |
| 9 (tests) | **Mock/LLM falso** + alguna llamada live | Evita gastar cuota en CI |
| 11 (demo) | `gemini-3.8-flash` si la cuota volvió; si no, `gemini-3.5-flash-lite` | Cumple la guía con respaldo |

**Regla:** el modelo se cambia **solo** en `.env` (`LLM_MODEL=...`); el código
nunca se toca porque siempre lee esa variable.

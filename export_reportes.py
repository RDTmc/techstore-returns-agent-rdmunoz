"""Exportación de resultados del agente TechStore Returns a PDF.

Funciones:
    generar_pdf(resultado)  -> bytes de documento PDF (reporte de la ejecución)
    guardar_copia_local(...) -> guarda PDF en disco (evidence/screenshots/)

El módulo es defensivo: si falta un campo en `resultado`, lo omite en lugar de fallar.
No depende de Streamlit, así que puede probarse también desde un script o CLI.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image as RLImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# --- Configuración ----------------------------------------------------------

ACCION_COLOR = {
    "aprobar_estandar": "#2e7d32",
    "aprobar_preferente": "#2e7d32",
    "solicitar_aprobacion": "#ef6c00",
    "escalar": "#c62828",
    "escalar_fraude": "#c62828",
    "solicitar_info": "#1565c0",
}
ACCION_ETIQUETA = {
    "aprobar_estandar": "APROBAR (ESTÁNDAR)",
    "aprobar_preferente": "APROBAR (PREFERENTE)",
    "solicitar_aprobacion": "SOLICITAR APROBACIÓN",
    "escalar": "ESCALAR",
    "escalar_fraude": "ESCALAR (FRAUDE)",
    "solicitar_info": "SOLICITAR INFORMACIÓN",
}

# Nombres del Paso 8.3 de la guía para los 3 escenarios conocidos
NOMBRES_PASO_83 = {
    "PED-001": "01_caso_estandar",
    "PED-015": "02_fuera_plazo",
    "PED-022": "03_alto_valor",
}

RUTA_EVIDENCIA = "evidence/screenshots"

_EMOJIS = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F000-\U0001F0FF"
    "\U00002B00-\U00002BFF"
    "\U0001F1E6-\U0001F1FF"
    "]+",
    flags=re.UNICODE,
)


def _texto(valor) -> str:
    """Convierte cualquier valor a texto plano sin emojis ni caracteres raros."""
    if valor is None:
        return ""
    if isinstance(valor, (dict, list)):
        valor = json.dumps(valor, ensure_ascii=False, default=str)
    texto = str(valor)
    texto = _EMOJIS.sub("", texto)
    return texto.strip()


def _texto_pdf(valor) -> str:
    """Texto apto para las fuentes base de ReportLab (latin-1)."""
    texto = _texto(valor)
    reemplazos = {"→": "->", "✓": "OK", "✗": "X", "·": "-", "“": '"', "”": '"', "’": "'"}
    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)
    return texto.encode("latin-1", "replace").decode("latin-1")


def nombre_base(pedido_id: str) -> str:
    """Nombre de archivo sin extensión: 01_caso_estandar para los 3 escenarios
    de la guía, o reporte_<pedido> para cualquier otro pedido."""
    return NOMBRES_PASO_83.get(pedido_id, f"reporte_{_texto(pedido_id)}")


# --- PDF (reportlab) --------------------------------------------------------


def _estilo(nombre: str, **kwargs) -> ParagraphStyle:
    base = getSampleStyleSheet()
    return ParagraphStyle(nombre, parent=base["Normal"], **kwargs)


def generar_pdf(resultado: dict) -> bytes:
    """Genera el reporte de la ejecución como PDF (uno por escenario)."""
    pedido_id = _texto_pdf(resultado.get("pedido_id"))
    pedido = resultado.get("pedido") or {}
    accion = _texto_pdf(resultado.get("accion", "sin_accion"))
    razon = _texto_pdf(resultado.get("razon"))
    color_hex = ACCION_COLOR.get(_texto(resultado.get("accion")), "#616161")
    color_accion = colors.HexColor(color_hex)

    estilos = {
        "titulo": _estilo("ts_titulo", fontName="Helvetica-Bold", fontSize=18,
                          textColor=colors.HexColor("#1a237e"), spaceAfter=2),
        "subtitulo": _estilo("ts_sub", fontSize=10, textColor=colors.HexColor("#616161")),
        "h2": _estilo("ts_h2", fontName="Helvetica-Bold", fontSize=12,
                      textColor=colors.HexColor("#424242"), spaceBefore=14, spaceAfter=6),
        "cuerpo": _estilo("ts_cuerpo", fontSize=10, leading=14),
        "accion": _estilo("ts_accion", fontName="Helvetica-Bold", fontSize=13,
                          textColor=colors.white, alignment=1, leading=16),
        "pie": _estilo("ts_pie", fontSize=8, textColor=colors.HexColor("#9e9e9e")),
    }

    story = [
        Paragraph("TechStore Returns — Reporte de devolución", estilos["titulo"]),
        Spacer(1, 14),
        Paragraph(
            f"Pedido {pedido_id} · Generado el "
            f"{datetime.now().strftime('%d-%m-%Y %H:%M')}",
            estilos["subtitulo"],
        ),
        Spacer(1, 14),
    ]

    # Banner de acción
    banner = Table(
        [[Paragraph(ACCION_ETIQUETA.get(_texto(resultado.get("accion")), accion.upper()),
                    estilos["accion"])]],
        colWidths=[16 * cm],
    )
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color_accion),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [banner, Spacer(1, 8)]

    story += [
        Paragraph("Razón de la decisión", estilos["h2"]),
        Paragraph(razon or "—", estilos["cuerpo"]),
    ]

    # Tabla resumen
    filas = [["Campo", "Valor"]]
    for clave in ("cliente", "fecha_compra", "dias_desde_compra", "monto", "categoria"):
        if clave in pedido:
            filas.append([
                Paragraph(clave.replace("_", " ").title(), estilos["cuerpo"]),
                Paragraph(_texto_pdf(pedido[clave]), estilos["cuerpo"]),
            ])
    if resultado.get("reembolso"):
        filas.append([
            Paragraph("Reembolso", estilos["cuerpo"]),
            Paragraph(
                f"{resultado['reembolso'].get('monto', 0):,} "
                f"{_texto_pdf(resultado['reembolso'].get('moneda'))}",
                estilos["cuerpo"],
            ),
        ])
    if resultado.get("etiqueta"):
        filas.append([
            Paragraph("Etiqueta de envío", estilos["cuerpo"]),
            Paragraph(_texto_pdf(resultado["etiqueta"].get("codigo")), estilos["cuerpo"]),
        ])
    historial = pedido.get("historial_cliente") or []
    filas.append([
        Paragraph("Devoluciones previas del cliente", estilos["cuerpo"]),
        Paragraph(str(len(historial)), estilos["cuerpo"]),
    ])

    tabla_resumen = Table(filas, colWidths=[6 * cm, 10 * cm], repeatRows=1)
    tabla_resumen.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eaf6")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdbdbd")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story += [Paragraph("Resumen de la ejecución", estilos["h2"]), tabla_resumen]

    # Trace / validación
    validacion = resultado.get("validacion")
    if validacion is not None:
        trace = _texto_pdf(validacion)
        story += [
            Paragraph("Razonamiento del agente (trace)", estilos["h2"]),
            Paragraph(trace or "—", estilos["cuerpo"]),
        ]

    # Historial del cliente
    if historial:
        cols = [c for c in ("fecha", "motivo", "monto") if historial[0].get(c)]
        h_datos = [[Paragraph(c.title(), estilos["cuerpo"]) for c in cols]]
        for fila in historial[:10]:
            h_datos.append([
                Paragraph(_texto_pdf(fila.get(c)), estilos["cuerpo"])
                for c in cols
            ])
        tabla_hist = Table(h_datos, colWidths=[3.5 * cm, 9 * cm, 3.5 * cm][: len(cols)],
                           repeatRows=1)
        tabla_hist.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eaf6")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdbdbd")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story += [Paragraph("Historial de devoluciones del cliente", estilos["h2"]),
                  tabla_hist]

    story += [Spacer(1, 16),
              Paragraph("Demo EP2 ISY0101 — Agente de devoluciones TechStore",
                        estilos["pie"])]

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                           topMargin=2 * cm, bottomMargin=2 * cm,
                           leftMargin=2 * cm, rightMargin=2 * cm,
                           title=f"Reporte {pedido_id}")
    doc.build(story)
    return buf.getvalue()


# --- Guardado local ---------------------------------------------------------


def guardar_copia_local(pdf: bytes, pedido_id: str,
                        ruta_base: str = RUTA_EVIDENCIA) -> list[str]:
    """Guarda el PDF en `ruta_base` con los nombres del Paso 8.3
    para los 3 escenarios de la guía (01_caso_estandar, 02_fuera_plazo,
    03_alto_valor) o reporte_<pedido> para cualquier otro."""
    import os

    os.makedirs(ruta_base, exist_ok=True)
    base = nombre_base(pedido_id)
    rutas = []
    if pdf:
        ruta_pdf = os.path.join(ruta_base, f"{base}.pdf")
        with open(ruta_pdf, "wb") as f:
            f.write(pdf)
        rutas.append(ruta_pdf)
    return rutas

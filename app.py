"""Interfaz Streamlit del agente TechStore Returns."""
import streamlit as st
import pandas as pd
from agent.core import procesar_solicitud
from agent.memory.short_term import crear_memoria_corto_plazo
from export_reportes import generar_pdf, guardar_copia_local, nombre_base

st.set_page_config(page_title="TechStore Returns Agent", page_icon="🤖", layout="wide")

if "memoria" not in st.session_state:
    st.session_state.memoria = crear_memoria_corto_plazo()
if "historial" not in st.session_state:
    st.session_state.historial = []

# --- Sidebar ---
with st.sidebar:
    st.title("🤖 TechStore Returns")
    st.caption("Agente de devoluciones — Demo EP2 ISY0101")
    st.markdown("### Casos de ejemplo")
    st.code("PED-001  → estándar\nPED-015  → fuera de plazo\nPED-022  → alto valor")
    if st.button("🔄 Nueva conversación"):
        st.session_state.historial = []
        st.session_state.memoria = crear_memoria_corto_plazo()
        st.session_state.pop("exportacion", None)
        st.rerun()

# --- Main ---
st.title("Agente de Devoluciones TechStore")
st.write("Simulación de automatización del proceso de devoluciones. "
         "Ingresa un ID de pedido para procesarlo.")

col1, col2 = st.columns([1, 2])
with col1:
    pedido_id = st.text_input("ID de pedido", value="PED-001")
    motivo = st.text_input("Motivo (opcional)", value="")
    ejecutar = st.button("▶️ Procesar devolución", type="primary")

if ejecutar:
    with st.spinner("El agente está razonando..."):
        resultado = procesar_solicitud(pedido_id, motivo)
    st.session_state.historial.append(resultado)

    # Generar el archivo de exportación (PDF) de esta ejecución
    if resultado.get("ok"):
        with st.spinner("Generando reporte PDF..."):
            st.session_state.exportacion = {
                "pedido_id": resultado.get("pedido_id", pedido_id),
                "pdf": generar_pdf(resultado),
            }

    # --- Resultados ---
if st.session_state.historial:
    ultimo = st.session_state.historial[-1]
    if not ultimo.get("ok"):
        st.error(f"❌ {ultimo.get('error')}")
    else:
        st.subheader(f"Resultado para {ultimo['pedido_id']}")

        # Banner de decisión
        colores = {
            "aprobar_estandar": "green",
            "aprobar_preferente": "green",
            "solicitar_aprobacion": "orange",
            "escalar": "red",
            "escalar_fraude": "red",
            "solicitar_info": "blue",
        }
        color = colores.get(ultimo["accion"], "gray")
        st.markdown(
            f"### :{color}[Acción: `{ultimo['accion']}`]"
        )
        st.caption(f"**Razón:** {ultimo['razon']}")

        # Detalles
        with st.expander("🔍 Razonamiento del agente (trace)", expanded=True):
            st.json({
                "pedido": ultimo.get("pedido"),
                "validacion": ultimo.get("validacion"),
                "accion": ultimo["accion"],
                "razon": ultimo["razon"],
            })

        with st.expander("🧠 Memoria recuperada del cliente"):
            st.write(f"Historial de devoluciones: "
                    f"{len(ultimo['pedido'].get('historial_cliente', []))}")
            st.dataframe(pd.DataFrame(ultimo['pedido'].get('historial_cliente', [])))

        if ultimo.get("reembolso"):
            st.success(f"💵 Reembolso: ${ultimo['reembolso']['monto']:,} {ultimo['reembolso']['moneda']}")
        if ultimo.get("etiqueta"):
            st.info(f"📦 Etiqueta: {ultimo['etiqueta']['codigo']}")

        # --- Exportar resultados (PDF de esta ejecución) ---
        exportacion = st.session_state.get("exportacion")
        if exportacion and exportacion.get("pedido_id") == ultimo["pedido_id"]:
            base = nombre_base(exportacion["pedido_id"])
            st.divider()
            st.subheader("📤 Exportar resultados")
            c_pdf, c_local = st.columns(2)
            with c_pdf:
                st.download_button(
                    "📄 Descargar PDF",
                    data=exportacion["pdf"],
                    file_name=f"{base}.pdf",
                    mime="application/pdf",
                )
            with c_local:
                if st.button("💾 Guardar copia local"):
                    rutas = guardar_copia_local(
                        exportacion["pdf"],
                        exportacion["pedido_id"],
                        ruta_base="evidence/screenshots",
                    )
                    st.success("Guardado en: " + "\n".join(rutas))
        else:
            st.info("Vuelve a procesar el pedido para generar los archivos de exportación.")


# --- Historial de la sesión ---
if st.session_state.historial:
    st.divider()
    st.subheader("📜 Historial de la sesión")
    df = pd.DataFrame([
        {"pedido": r["pedido_id"], "acción": r["accion"], "razón": r["razon"]}
        for r in st.session_state.historial if r.get("ok")
    ])
    st.dataframe(df, width="stretch")

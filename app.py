import streamlit as st
import pandas as pd
from sti_lib import STI_Core, ProtocoloError

# Configuración de página
st.set_page_config(page_title="STI v2.0", layout="wide")

st.title("Sistema de Traducción Isomórfica v2.0")
[span_8](start_span)st.markdown("Protocolo Determinista: *El usuario es la máxima autoridad*[span_8](end_span)")

# Inicializar el Core en la sesión (Estado persistente)
if 'sti' not in st.session_state:
    st.session_state.sti = STI_Core()

# -[span_9](start_span)-- SIDEBAR: Comandos[span_9](end_span) ---
st.sidebar.header("Panel de Control (P11)")
modo_salida = st.sidebar.radio("Modo de Salida", ["BORRADOR", "FINAL"])
st.sidebar.info(f"Estado: {st.session_state.sti.status}")

# -[span_10](start_span)-- FASE 1: INPUT[span_10](end_span) ---
st.header("1. Input Texto Fuente")
text_input = st.text_area("Introduce el texto en árabe/fuente:", height=150)

if st.button("Iniciar Protocolo (Limpieza P10.A + Análisis P8.A)"):
    st.session_state.sti.p10_a_limpieza(text_input)
    res = st.session_state.sti.p8_a_analisis_lexico()
    st.success(res)

# --- FASE 2: GESTIÓN DE GLOSARIO (P8) ---
if st.session_state.sti.glossary:
    st.header("2. Gestión de Glosario (P8)")
    st.warning("⚠️ Recuerda: Los NÚCLEOS son invariables. Las PARTÍCULAS se resuelven dinámicamente si se dejan vacías.")
    
    # Convertir glosario a DataFrame para edición fácil
    df = pd.DataFrame.from_dict(st.session_state.sti.glossary, orient='index')
    
    # Mostrar editor de datos editable
    edited_df = st.data_editor(
        df[['categoria', 'token_tgt', 'status']], 
        key="editor_glosario",
        use_container_width=True
    )
    
    # Botón para guardar cambios del usuario en el Core
    if st.button("💾 Actualizar Glosario (Comando ACTUALIZA)"):
        # Actualizamos el objeto core con los datos editados
        for token, row in edited_df.iterrows():
            st.session_state.sti.glossary[token]['token_tgt'] = row['token_tgt']
            st.session_state.sti.glossary[token]['categoria'] = row['categoria']
            # Si el usuario puso traducción, cambiamos status a ASIGNADO
            if row['token_tgt'].strip() != "":
                st.session_state.sti.glossary[token]['status'] = "ASIGNADO"
        st.success("Glosario actualizado. Listo para verificar integridad.")

# --- FASE 3: TRADUCCIÓN (P3) ---
st.header("3. Core de Traducción (P3-P7)")

if st.button("EJECUTAR TRADUCCIÓN"):
    try:
        msg = st.session_state.sti.p3_traduccion()
        st.success(msg)
    except ProtocoloError as e:
        [span_11](start_span)st.error(f"⛔ {e}") # Muestra el Fallo Crítico[span_11](end_span)

# --- FASE 4: OUTPUT (P10.B) ---
if st.session_state.sti.status == "TRADUCIDO":
    st.header("4. Output Final")
    texto_final = st.session_state.sti.p10_b_renderizado()
    st.text_area("Resultado:", value=texto_final, height=150)

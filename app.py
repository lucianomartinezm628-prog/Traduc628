import streamlit as st
import pandas as pd
from io import StringIO
from sti_lib import STI_Core, ProtocoloError

st.set_page_config(page_title="STI v2.0", layout="wide")
st.title("Sistema de Traducción Isomórfica v2.0")

# Inicializar Memoria
if 'sti' not in st.session_state:
    st.session_state.sti = STI_Core()

# --- SIDEBAR ---
st.sidebar.header("Control P11")
st.sidebar.info(f"Estado: {st.session_state.sti.status}")

# Terminal de Comandos
cmd = st.sidebar.text_input("Comando:", placeholder="[AÑADE token=trad]")
if st.sidebar.button("Ejecutar"):
    if "=" in cmd and "[AÑADE" in cmd:
        try:
            clean = cmd.replace("[AÑADE", "").replace("]", "")
            t, trad = clean.split("=")
            st.session_state.sti.glossary[t.strip()] = {
                "token_src": t.strip(), "token_tgt": trad.strip(),
                "categoria": "NUCLEO", "status": "ASIGNADO", "ocurrencias": []
            }
            st.sidebar.success(f"Añadido: {t.strip()}")
        except: st.sidebar.error("Error de formato.")
    elif "[REINICIAR]" in cmd:
        st.session_state.sti = STI_Core()
        st.rerun()

# Carga de Glosario TXT
uploaded = st.sidebar.file_uploader("Cargar Glosario (.txt)", type="txt")
if uploaded:
    stringio = StringIO(uploaded.getvalue().decode("utf-8"))
    for line in stringio:
        if "=" in line:
            t, trad = line.split("=", 1)
            st.session_state.sti.glossary[t.strip()] = {
                "token_src": t.strip(), "token_tgt": trad.strip(),
                "categoria": "NUCLEO", "status": "ASIGNADO", "ocurrencias": []
            }
    st.sidebar.success("Glosario importado.")

# --- FASE 1: INPUT ---
st.header("1. Input")
txt = st.text_area("Texto Fuente:", height=100)
if st.button("Iniciar (P10.A + P8.A)"):
    st.session_state.sti.p10_a_limpieza(txt)
    msg = st.session_state.sti.p8_a_analisis_lexico()
    st.success(msg)

# --- FASE 2: GLOSARIO ---
if st.session_state.sti.glossary:
    st.header("2. Glosario")
    
    # IA AUTOCOMPLETAR
    with st.expander("🤖 IA Autocompletar"):
        key = st.text_input("API Key Gemini:", type="password")
        if st.button("Ejecutar IA") and key:
            res = st.session_state.sti.p8_ia_autocompletar(key)
            st.success(res)
            st.rerun()

    # EDITOR
    df = pd.DataFrame.from_dict(st.session_state.sti.glossary, orient='index')
    edited = st.data_editor(df[['categoria', 'token_tgt', 'status']], use_container_width=True)
    
    if st.button("Guardar Cambios Manuales"):
        for t, row in edited.iterrows():
            st.session_state.sti.glossary[t]['token_tgt'] = row['token_tgt']
            st.session_state.sti.glossary[t]['categoria'] = row['categoria']
            if row['token_tgt']: st.session_state.sti.glossary[t]['status'] = "ASIGNADO"
        st.success("Guardado.")

# --- FASE 3: TRADUCCION ---
st.header("3. Traducción")
if st.button("TRADUCIR (P3)"):
    try:
        msg = st.session_state.sti.p3_traduccion()
        st.success(msg)
    except ProtocoloError as e:
        st.error(f"⛔ {e}")

# --- FASE 4: SALIDA ---
if st.session_state.sti.status == "TRADUCIDO":
    st.header("4. Resultado")
    st.text_area("Final:", st.session_state.sti.p10_b_renderizado())

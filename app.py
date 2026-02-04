import streamlit as st
import pandas as pd
from sti_lib import STI_Core, ProtocoloError

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="STI v2.0", layout="wide")

st.title("Sistema de Traducción Isomórfica v2.0")
st.markdown("Protocolo Determinista: *El usuario es la máxima autoridad*")

# Inicializar el Core (Memoria persistente)
if 'sti' not in st.session_state:
    st.session_state.sti = STI_Core()

# --- SIDEBAR: PANEL DE CONTROL Y COMANDOS (P11) ---
st.sidebar.header("Panel de Control (P11)")

# 1. Estado del sistema
st.sidebar.info(f"Fase Actual: {st.session_state.sti.status}")

# 2. Terminal de Comandos (¡NUEVO!)
st.sidebar.markdown("### Terminal de Comandos")
cmd_input = st.sidebar.text_input("Escribir comando:", placeholder="Ej: [AÑADE nomen=nombre]")

if st.sidebar.button("Ejecutar Comando"):
    # Lógica básica para procesar comandos manuales
    try:
        cmd = cmd_input.strip()
        
        # Comando [AÑADE x=y]
        if cmd.startswith("[AÑADE") and "=" in cmd:
            parts = cmd.replace("[AÑADE", "").replace("]", "").split("=")
            token = parts[0].strip()
            traduccion = parts[1].strip()
            
            # Registrar en el núcleo
            st.session_state.sti.glossary[token] = {
                "token_src": token,
                "token_tgt": traduccion,
                "categoria": "NUCLEO", # Asumimos núcleo por defecto al añadir manual
                "status": "ASIGNADO",
                "ocurrencias": []
            }
            st.sidebar.success(f"Comando ejecutado: Asignado '{token}' -> '{traduccion}'")
            
        # Comando [ELIMINA x]
        elif cmd.startswith("[ELIMINA"):
            token = cmd.replace("[ELIMINA", "").replace("]", "").strip()
            if token in st.session_state.sti.glossary:
                del st.session_state.sti.glossary[token]
                st.sidebar.warning(f"Comando ejecutado: Eliminado '{token}'")
            else:
                st.sidebar.error("Token no encontrado.")
                
        # Comando [REINICIAR]
        elif cmd == "[REINICIAR]":
            st.session_state.sti = STI_Core()
            st.sidebar.warning("Sistema reiniciado.")
            st.rerun() # Recarga la página
            
        else:
            st.sidebar.error("Comando no reconocido o formato incorrecto.")
            
    except Exception as e:
        st.sidebar.error(f"Error al ejecutar: {e}")

# 3. Configuración de Salida
modo_salida = st.sidebar.radio("Modo de Salida", ["BORRADOR", "FINAL"])


# --- FASE 1: INPUT ---
st.header("1. Input Texto Fuente")
text_input = st.text_area("Introduce el texto fuente:", height=150)

if st.button("Iniciar Protocolo (Limpieza P10.A + Análisis P8.A)"):
    st.session_state.sti.p10_a_limpieza(text_input)
    res = st.session_state.sti.p8_a_analisis_lexico()
    st.success(res)

# --- FASE 2: GESTIÓN DE GLOSARIO (P8) ---
if st.session_state.sti.glossary:
    st.header("2. Gestión de Glosario (P8)")
    st.warning("⚠️ Recuerda: Los NÚCLEOS son invariables. Las PARTÍCULAS se resuelven dinámicamente.")
    
    # Crear DataFrame para el editor visual
    df = pd.DataFrame.from_dict(st.session_state.sti.glossary, orient='index')
    
    # Editor visual (Grid)
    edited_df = st.data_editor(
        df[['categoria', 'token_tgt', 'status']], 
        key="editor_glosario",
        use_container_width=True
    )
    
    # Botón visual para guardar cambios masivos (Equivale a muchos comandos ACTUALIZA)
    if st.button("💾 Guardar Cambios del Glosario"):
        cambios_count = 0
        for token, row in edited_df.iterrows():
            # Actualizar solo si hubo cambios
            if st.session_state.sti.glossary[token]['token_tgt'] != row['token_tgt']:
                st.session_state.sti.glossary[token]['token_tgt'] = row['token_tgt']
                st.session_state.sti.glossary[token]['categoria'] = row['categoria']
                if row['token_tgt'].strip() != "":
                    st.session_state.sti.glossary[token]['status'] = "ASIGNADO"
                cambios_count += 1
        
        if cambios_count > 0:
            st.success(f"Glosario actualizado: {cambios_count} cambios registrados.")
        else:
            st.info("No se detectaron cambios nuevos.")

# --- FASE 3: TRADUCCIÓN (P3) ---
st.header("3. Core de Traducción (P3-P7)")

if st.button("EJECUTAR TRADUCCIÓN"):
    try:
        msg = st.session_state.sti.p3_traduccion()
        st.success(msg)
    except ProtocoloError as e:
        st.error(f"⛔ FALLO CRÍTICO: {e}")

# --- FASE 4: OUTPUT (P10.B) ---
if st.session_state.sti.status == "TRADUCIDO":
    st.header("4. Output Final")
    texto_final = st.session_state.sti.p10_b_renderizado()
    st.text_area("Resultado:", value=texto_final, height=150)

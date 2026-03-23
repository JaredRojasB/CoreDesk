import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CoreDesk AI Support", page_icon="🖥️", layout="centered")

# --- 1. CONFIGURACIÓN DE IA (Nube o Local) ---
load_dotenv()
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ Error: Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=api_key)

# Inicializar modelo automático
if "model_name" not in st.session_state:
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.session_state.model_name = next((m for m in modelos if "flash" in m), modelos[0])
    except:
        st.session_state.model_name = "gemini-1.5-flash"

model = genai.GenerativeModel(st.session_state.model_name)

# --- 2. FUNCIONES DE GUARDADO (Bitácora) ---
def guardar_en_bitacora(nombre, empresa, problema, respuesta):
    archivo_bitacora = "bitacora_coredesk.csv"
    nueva_entrada = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuario": nombre,
        "Empresa": empresa,
        "Problema": problema,
        "Solucion_IA": respuesta
    }
    
    df_nueva = pd.DataFrame([nueva_entrada])
    
    if not os.path.isfile(archivo_bitacora):
        df_nueva.to_csv(archivo_bitacora, index=False, encoding='utf-8')
    else:
        df_nueva.to_csv(archivo_bitacora, mode='a', header=False, index=False, encoding='utf-8')

# --- 3. GESTIÓN DE ESTADO ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# --- PANTALLA DE REGISTRO ---
if st.session_state.user_data is None:
    st.title("🛡️ Registro de Incidencia - CoreDesk")
    st.markdown("Bienvenido al sistema de soporte inteligente de **CUCEA**.")
    with st.form("registro"):
        nombre = st.text_input("Nombre Completo:")
        empresa = st.text_input("Empresa/Departamento:")
        submit = st.form_submit_button("Iniciar Soporte")
        
        if submit:
            if nombre and empresa:
                st.session_state.user_data = {"nombre": nombre, "empresa": empresa}
                st.rerun()
            else:
                st.error("Por favor, llena todos los campos.")
else:
    # --- INTERFAZ DE CHAT ---
    st.title("🖥️ CoreDesk Support AI")
    st.caption(f"Sesión activa: {st.session_state.user_data['nombre']} | {st.session_state.user_data['empresa']}")

    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del usuario
    if prompt := st.chat_input("Describe tu problema técnico..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Respuesta de la IA
        with st.chat_message("assistant"):
            with st.spinner("Analizando con CoreDesk AI..."):
                try:
                    contexto = f"""
                    Eres el experto de Soporte Técnico de CoreDesk. 
                    Usuario: {st.session_state.user_data['nombre']} de la empresa {st.session_state.user_data['empresa']}.
                    
                    REGLAS:
                    1. Identifícate como 'Asistente IA de CoreDesk'.
                    2. Usa negritas y listas para que sea visual.
                    3. Al final, pregunta siempre: '¿Te funcionó la información que te di?'
                    """
                    
                    chat = model.start_chat(history=[])
                    response = chat.send_message(f"{contexto}\nProblema: {prompt}")
                    respuesta_final = response.text
                    
                    st.markdown(respuesta_final)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta_final})
                    
                    # GUARDAR EN BITÁCORA AUTOMÁTICAMENTE
                    guardar_en_bitacora(
                        st.session_state.user_data['nombre'],
                        st.session_state.user_data['empresa'],
                        prompt,
                        respuesta_final
                    )
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    # --- BARRA LATERAL (ADMIN) ---
    with st.sidebar:
        st.header("Opciones")
        if st.button("Cerrar Ticket / Nuevo Usuario"):
            st.session_state.user_data = None
            st.session_state.messages = []
            st.rerun()
            
        st.markdown("---")
        st.subheader("Zona Admin")
        if os.path.exists("bitacora_coredesk.csv"):
            df_log = pd.read_csv("bitacora_coredesk.csv")
            st.download_button(
                label="Descargar Bitácora (CSV)",
                data=df_log.to_csv(index=False).encode('utf-8'),
                file_name="bitacora_coredesk.csv",
                mime="text/csv"
            )
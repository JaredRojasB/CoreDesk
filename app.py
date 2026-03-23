import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="CoreDesk Support AI", 
    page_icon="Logo CoreDesk.png", 
    layout="centered"
)

# --- 2. DISEÑO PERSONALIZADO (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f7f9;
    }
    .main-header {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #0E3255;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        color: #6c757d;
        font-size: 18px;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    .stButton>button {
        border-radius: 20px;
        background-color: #0E3255;
        color: white;
        font-weight: bold;
        height: 3em;
        width: 100%;
    }
    /* Estilo de los globos de chat */
    .stChatMessage {
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE IA ---
load_dotenv()
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ Error: Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=api_key)

if "model_name" not in st.session_state:
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.session_state.model_name = next((m for m in modelos if "flash" in m), modelos[0])
    except:
        st.session_state.model_name = "gemini-1.5-flash"

model = genai.GenerativeModel(st.session_state.model_name)

# --- 4. FUNCIONES DE BITÁCORA ---
def guardar_en_bitacora(nombre, empresa, problema, respuesta):
    archivo_bitacora = "bitacora_coredesk.csv"
    nueva_entrada = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuario": nombre,
        "Empresa": empresa,
        "Problema": problema,
        "Solucion_IA": respuesta.replace('\n', ' ')
    }
    df_nueva = pd.DataFrame([nueva_entrada])
    if not os.path.isfile(archivo_bitacora):
        df_nueva.to_csv(archivo_bitacora, index=False, encoding='utf-8')
    else:
        df_nueva.to_csv(archivo_bitacora, mode='a', header=False, index=False, encoding='utf-8')

# --- 5. GESTIÓN DE SESIÓN ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# --- 6. CABECERA (LOGO + TÍTULO) ---
# Aquí es donde referenciamos tu imagen
col1, col2 = st.columns([1, 4])
with col1:
    try:
        # IMPORTANTE: Asegúrate de que el archivo se llame exactamente 'logo.png' en Codespaces
        logo_img = Image.open("logo.png")
        st.image(logo_img, width=100)
    except Exception as e:
        # Si no encuentra la imagen, pone un icono por defecto para que no truene el código
        st.markdown("<h1 style='font-size: 60px;'>🛡️</h1>", unsafe_allow_html=True)

with col2:
    st.markdown("<p class='main-header'>CoreDesk</p>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Intelligent IT Management System</p>", unsafe_allow_html=True)

# --- 7. LÓGICA DE NAVEGACIÓN ---
if st.session_state.user_data is None:
    st.info("👋 Bienvenido al portal de soporte. Identifícate para continuar.")
    with st.form("login_form"):
        nombre = st.text_input("Nombre Completo:")
        empresa = st.text_input("Empresa o Departamento:")
        if st.form_submit_button("INGRESAR"):
            if nombre and empresa:
                st.session_state.user_data = {"nombre": nombre, "empresa": empresa}
                st.rerun()
            else:
                st.warning("Por favor completa ambos campos.")
else:
    # Mostrar Chat
    st.write(f"Sesión iniciada: **{st.session_state.user_data['nombre']}** | **{st.session_state.user_data['empresa']}**")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("¿Cómo puedo ayudarte con tu equipo hoy?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analizando incidencia..."):
                try:
                    contexto = f"""
                    Eres el experto de Soporte Técnico de CoreDesk. 
                    Usuario: {st.session_state.user_data['nombre']} de {st.session_state.user_data['empresa']}.
                    1. Identifícate como 'Asistente IA de CoreDesk'.
                    2. Usa negritas y listas.
                    3. Al final pregunta: '¿Te funcionó la información que te di?'
                    """
                    chat = model.start_chat(history=[])
                    response = chat.send_message(f"{contexto}\nProblema: {prompt}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    guardar_en_bitacora(st.session_state.user_data['nombre'], st.session_state.user_data['empresa'], prompt, response.text)
                except Exception as e:
                    st.error(f"Error: {e}")

# --- 8. BARRA LATERAL (ADMIN) ---
with st.sidebar:
    st.title("Panel IT")
    if st.button("Finalizar Ticket"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    if os.path.exists("bitacora_coredesk.csv"):
        df_log = pd.read_csv("bitacora_coredesk.csv")
        st.download_button(
            label="📥 Descargar Bitácora",
            data=df_log.to_csv(index=False).encode('utf-8'),
            file_name="bitacora_coredesk.csv",
            mime="text/csv"
        )
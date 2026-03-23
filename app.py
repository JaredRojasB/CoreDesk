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
    page_icon="🛡️", 
    layout="centered"
)

# --- 2. DISEÑO PERSONALIZADO (CSS) ---
st.markdown("""
    <style>
    /* Estilo para los contenedores de mensajes */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    /* Estilo del título principal */
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
    /* Botones más modernos */
    .stButton>button {
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE IA ---
load_dotenv()
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Falta API KEY")
    st.stop()
genai.configure(api_key=api_key)

if "model_name" not in st.session_state:
    st.session_state.model_name = "gemini-1.5-flash"
model = genai.GenerativeModel(st.session_state.model_name)

# --- 4. FUNCIONES Y ESTADO ---
def guardar_en_bitacora(nombre, empresa, problema, respuesta):
    archivo = "bitacora_coredesk.csv"
    nueva_entrada = pd.DataFrame([{
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuario": nombre, "Empresa": empresa, "Problema": problema, "Solucion": respuesta.replace('\n', ' ')
    }])
    if not os.path.isfile(archivo):
        nueva_entrada.to_csv(archivo, index=False)
    else:
        nueva_entrada.to_csv(archivo, mode='a', header=False, index=False)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# --- 5. CABECERA CON LOGO ---
col1, col2 = st.columns([1, 4])
with col1:
    try:
        # Cambia 'logo.png' por el nombre exacto de tu archivo
        image = Image.open('logo.png') 
        st.image(image, width=100)
    except:
        st.write("🛡️") # Emoji de respaldo si no encuentra la imagen

with col2:
    st.markdown("<p class='main-header'>CoreDesk</p>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Intelligent IT Management System</p>", unsafe_allow_html=True)

# --- 6. LÓGICA DE NAVEGACIÓN ---
if st.session_state.user_data is None:
    st.info("👋 Bienvenido. Por favor, inicia sesión para reportar un problema.")
    with st.form("registro"):
        nombre = st.text_input("Nombre:")
        empresa = st.text_input("Empresa:")
        if st.form_submit_button("INGRESAR"):
            if nombre and empresa:
                st.session_state.user_data = {"nombre": nombre, "empresa": empresa}
                st.rerun()

else:
    # Interfaz de Chat
    st.write(f"Atendiendo a: **{st.session_state.user_data['nombre']}** ({st.session_state.user_data['empresa']})")
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("¿En qué te ayudo?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("CoreDesk pensando..."):
                ctx = f"Eres Soporte CoreDesk. Usuario: {st.session_state.user_data['nombre']}. Sé visual y pregunta al final si funcionó."
                res = model.start_chat(history=[]).send_message(f"{ctx}\nProblema: {prompt}").text
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
                guardar_en_bitacora(st.session_state.user_data['nombre'], st.session_state.user_data['empresa'], prompt, res)

    # Sidebar Admin
    with st.sidebar:
        st.title("Panel IT")
        if st.button("Nuevo Ticket"):
            st.session_state.user_data = None
            st.session_state.messages = []
            st.rerun()
        if os.path.exists("bitacora_coredesk.csv"):
            st.download_button("Descargar Reportes", pd.read_csv("bitacora_coredesk.csv").to_csv(index=False), "reporte.csv")
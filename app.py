import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import re
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
    .stApp {
        background-color: #f4f7f9;
    }
    .main-title {
        color: #0E3255;
        font-size: 50px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0px;
    }
    .banner-container {
        text-align: center;
        padding: 20px;
    }
    /* Estilo de botones */
    .stButton>button {
        border-radius: 10px;
        background-color: #0E3255;
        color: white;
        font-weight: bold;
        transition: 0.3s;
        border: 2px solid #0E3255;
    }
    .stButton>button:hover {
        background-color: #ffffff;
        color: #0E3255;
    }
    /* Botón de finalizar (Rojo) */
    div[data-testid="stSidebar"] .stButton>button {
        background-color: #d9534f;
        border-color: #d9534f;
    }
    /* Chat bubbles */
    .stChatMessage {
        border-radius: 20px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE IA ---
load_dotenv()
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ Configura la API KEY en Secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- 4. FUNCIONES DE VALIDACIÓN Y BITÁCORA ---
def es_correo_valido(correo):
    # Regex para validar dominios específicos
    patron = r'^[a-zA-Z0-9_.+-]+@(gmail\.com|outlook\.com|hotmail\.com)$'
    return re.match(patron, correo)

def guardar_en_bitacora(nombre, empresa, correo, problema, respuesta):
    archivo = "bitacora_coredesk.csv"
    nueva_entrada = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuario": nombre,
        "Empresa": empresa,
        "Correo": correo,
        "Problema": problema,
        "Solucion_IA": respuesta.replace('\n', ' ')
    }
    df = pd.DataFrame([nueva_entrada])
    if not os.path.isfile(archivo):
        df.to_csv(archivo, index=False, encoding='utf-8')
    else:
        df.to_csv(archivo, mode='a', header=False, index=False, encoding='utf-8')

# --- 5. GESTIÓN DE SESIÓN ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# --- 6. PANTALLA PRINCIPAL (BANNER) ---
with st.container():
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        try:
            logo_img = Image.open("logo.png")
            st.image(logo_img, use_container_width=True)
        except:
            st.markdown("<h1 style='text-align: center;'>🛡️</h1>", unsafe_allow_html=True)
    st.markdown("<p class='main-title'>CoreDesk</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6c757d;'>Sistema de Soporte Técnico Inteligente</p>", unsafe_allow_html=True)

# --- 7. LÓGICA DE REGISTRO / CHAT ---
if st.session_state.user_data is None:
    st.markdown("---")
    with st.form("registro_form"):
        st.subheader("📝 Apertura de Ticket")
        nombre = st.text_input("Nombre Completo:")
        empresa = st.text_input("Empresa / Departamento:")
        correo = st.text_input("Correo Electrónico (Gmail, Outlook, Hotmail):")
        
        btn_ingresar = st.form_submit_button("INICIAR SOPORTE")
        
        if btn_ingresar:
            if not nombre or not empresa or not correo:
                st.error("❌ Por favor, llena todos los campos.")
            elif not es_correo_valido(correo):
                st.error("❌ Ingresa un correo válido (Gmail, Outlook o Hotmail).")
            else:
                st.session_state.user_data = {"nombre": nombre, "empresa": empresa, "correo": correo}
                st.success("✅ Datos validados correctamente.")
                st.rerun()

else:
    # --- INTERFAZ DE CHAT ACTIVA ---
    st.markdown(f"**Usuario:** {st.session_state.user_data['nombre']} | **Empresa:** {st.session_state.user_data['empresa']}")
    
    # Botón (Inactivo por ahora) para subir imágenes
    st.file_uploader("📷 Adjuntar imagen del problema (Próximamente)", type=["png", "jpg", "jpeg"], disabled=True)

    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de chat
    if prompt := st.chat_input("Describe paso a paso tu problema..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("CoreDesk AI analizando solución técnica..."):
                try:
                    system_prompt = f"""
                    Eres el experto senior de Soporte Técnico de CoreDesk. 
                    Atiendes a {st.session_state.user_data['nombre']} de {st.session_state.user_data['empresa']}.
                    
                    REGLAS DE RESPUESTA:
                    1. Identifícate como 'Asistente IA de CoreDesk'.
                    2. Responde con un formato de 'GUÍA PASO A PASO'.
                    3. Usa negritas para componentes de hardware o comandos de software.
                    4. Sé extremadamente específico en las acciones (Ej: 'Presiona la tecla Windows + R', no solo 'abre ejecutar').
                    5. Organiza la información en secciones: 'Diagnóstico Inicial' y 'Pasos a seguir'.
                    6. Al final pregunta: '¿Te funcionó la información que te di?'
                    """
                    chat = model.start_chat(history=[])
                    response = chat.send_message(f"{system_prompt}\nProblema: {prompt}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    guardar_en_bitacora(
                        st.session_state.user_data['nombre'], 
                        st.session_state.user_data['empresa'], 
                        st.session_state.user_data['correo'],
                        prompt, 
                        response.text
                    )
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.title("⚙️ Panel de Usuario")
        st.write(f"Conectado como: **{st.session_state.user_data['correo']}**")
        
        # Botón para finalizar chat (Rojo y visible)
        if st.button("🔴 FINALIZAR SOPORTE"):
            st.session_state.user_data = None
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        if os.path.exists("bitacora_coredesk.csv"):
            df_log = pd.read_csv("bitacora_coredesk.csv")
            st.download_button(
                label="📥 Descargar Reportes (Admin)",
                data=df_log.to_csv(index=False).encode('utf-8'),
                file_name="bitacora_coredesk.csv",
                mime="text/csv"
            )
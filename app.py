import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import re
import time
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
    /* Estilo de botones */
    .stButton>button {
        border-radius: 10px;
        background-color: #0E3255;
        color: white;
        font-weight: bold;
        transition: 0.3s;
        border: 2px solid #0E3255;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #ffffff;
        color: #0E3255;
    }
    /* Estilo de los Chat Bubbles */
    .stChatMessage {
        border-radius: 20px;
    }
    /* Personalización del Spinner */
    .stSpinner > div {
        border-top-color: #0E3255 !important;
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

# --- 4. FUNCIONES ---
def es_correo_valido(correo):
    patron = r'^[a-zA-Z0-9_.+-]+@(gmail\.com|outlook\.com|hotmail\.com)$'
    return re.match(patron, correo)

def guardar_en_bitacora(nombre, empresa, correo, problema, respuesta):
    archivo = "bitacora_coredesk.csv"
    nueva_entrada = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuario": nombre, "Empresa": empresa, "Correo": correo,
        "Problema": problema, "Solucion_IA": respuesta.replace('\n', ' ')
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

# --- 6. BANNER PRINCIPAL ---
with st.container():
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        try:
            # Asegúrate de que el archivo se llame exactamente 'logo.png'
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
            # --- AQUÍ ESTÁ LA SOLUCIÓN ---
            # Envolvemos TODA la validación en el spinner
            with st.spinner("Validando credenciales en el servidor CoreDesk..."):
                # Pequeña pausa forzada para que el usuario alcance a ver la animación
                # y sienta que el sistema está trabajando.
                time.sleep(1) 
                
                if not nombre or not empresa or not correo:
                    st.error("❌ Por favor, llena todos los campos.")
                elif not es_correo_valido(correo):
                    st.error("❌ Ingresa un correo válido (Gmail, Outlook o Hotmail).")
                else:
                    # Si todo está bien, guardamos y recargamos
                    st.session_state.user_data = {"nombre": nombre, "empresa": empresa, "correo": correo}
                    st.success("✅ Acceso concedido.")
                    st.rerun()

else:
    # --- INTERFAZ DE CHAT ---
    st.markdown(f"**Sesión:** {st.session_state.user_data['nombre']} | **Soporte:** {st.session_state.user_data['empresa']}")
    
    st.file_uploader("📷 Adjuntar evidencia (Deshabilitado)", type=["png", "jpg"], disabled=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Describe tu problema paso a paso..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Carga mientras la IA "piensa"
        with st.chat_message("assistant"):
            with st.spinner("CoreDesk AI analizando hardware y software..."):
                try:
                    system_prompt = f"""
                    Eres el experto senior de Soporte Técnico de CoreDesk. 
                    Guía PASO A PASO a {st.session_state.user_data['nombre']}.
                    Usa negritas para componentes de hardware o comandos de software.
                    Al final pregunta: '¿Te funcionó la información que te di?'
                    """
                    chat = model.start_chat(history=[])
                    response = chat.send_message(f"{system_prompt}\nProblema: {prompt}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    guardar_en_bitacora(
                        st.session_state.user_data['nombre'], 
                        st.session_state.user_data['empresa'], 
                        st.session_state.user_data['correo'],
                        prompt, response.text
                    )
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("⚙️ Panel de Usuario")
        if st.button("🔴 FINALIZAR SOPORTE"):
            with st.spinner("Cerrando ticket de forma segura..."):
                time.sleep(0.5)
                st.session_state.user_data = None
                st.session_state.messages = []
                st.rerun()
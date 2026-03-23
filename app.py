import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="centered")

# Estilos inyectados (Los básicos que funcionan)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3em;
        background-color: #0E3255; color: white; font-weight: bold;
    }
    /* Ocultar iconos naranja basura de Streamlit */
    [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u, span[data-testid="stWidgetLabel"] { 
        display: none !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DE IA ---
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

# Logo
try: logo_img = Image.open("logo.png")
except: logo_img = None

# --- 3. INTERFAZ ---

# Caso A: Registro
if st.session_state.user_data is None:
    if logo_img: st.image(logo_img, width=200)
    st.markdown("<h1 style='color:#0E3255; text-align:center;'>🛡️ CoreDesk System</h1>", unsafe_allow_html=True)
    
    with st.form("registro"):
        nombre = st.text_input("Nombre Completo:")
        empresa = st.text_input("Empresa:")
        if st.form_submit_button("INGRESAR AL SISTEMA"):
            if nombre and empresa:
                st.session_state.user_data = {"nombre": nombre, "empresa": empresa}
                st.rerun()

# Caso B: Chat (El que SÍ responde)
else:
    st.markdown(f"<h2 style='color:#0E3255;'>Soporte: {st.session_state.user_data['empresa']}</h2>", unsafe_allow_html=True)
    st.caption(f"Atendiendo a: **{st.session_state.user_data['nombre']}**")

    # Mostrar Historial
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # CAJA DE ENTRADA (Lógica pura de Streamlit)
    if prompt := st.chat_input("¿Cuál es el problema técnico hoy?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    # System Prompt para ser amable y procedimental
                    ctx = f"""Eres el experto de Soporte Técnico de CoreDesk. 
                    Ayudas a {st.session_state.user_data['nombre']} de {st.session_state.user_data['empresa']}.
                    Explica paso a paso como para alguien novato (ej: 'Abre la carpeta naranja').
                    Usa negritas y pregunta al final: '¿Te funcionó la información que te di?'"""
                    
                    response = model.generate_content(f"{ctx}\n\nProblema: {prompt}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")

    # Botón lateral para salir
    if st.sidebar.button("Finalizar Ticket"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.rerun()
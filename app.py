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

# --- 2. CONFIGURACIÓN DE IA (SOLUCIÓN DEFINITIVA AL 404) ---
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Lógica para encontrar el nombre exacto del modelo que Google permite en tu cuenta
if "model_name" not in st.session_state:
    try:
        # Listamos los modelos y buscamos el que tenga 'flash' en el nombre
        modelos_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.session_state.model_name = next((m for m in modelos_disponibles if "flash" in m), modelos_disponibles[0])
    except Exception:
        # Si falla el listado, usamos el nombre estándar como último recurso
        st.session_state.model_name = "gemini-1.5-flash"

model = genai.GenerativeModel(st.session_state.model_name)

# Usamos el nombre del modelo sin el prefijo 'models/' para mayor compatibilidad
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

# Caso B: Chat
else:
    st.markdown(f"<h2 style='color:#0E3255;'>Soporte: {st.session_state.user_data['empresa']}</h2>", unsafe_allow_html=True)
    st.caption(f"Atendiendo a: **{st.session_state.user_data['nombre']}**")

    # Mostrar Historial con Avatares fijos
    for m in st.session_state.messages:
        # Forzamos avatar de emoji para evitar el error visual
        avatar_type = "🤖" if m["role"] == "assistant" else "👤"
        with st.chat_message(m["role"], avatar=avatar_type):
            st.markdown(m["content"])

    # CAJA DE ENTRADA
    if prompt := st.chat_input("¿Cuál es el problema técnico hoy?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    # System Prompt procedimental para novatos
                    ctx = f"""Eres el experto de Soporte Técnico de CoreDesk. 
                    Ayudas a {st.session_state.user_data['nombre']} de {st.session_state.user_data['empresa']}.
                    Explica paso a paso como para alguien novato.
                    Ejemplo: 'Abre la carpeta naranja abajo en la barra' o 'Presiona Ctrl+R'.
                    Usa negritas y pregunta al final: '¿Te funcionó la información que te di?'"""
                    
                    # Generación de contenido
                    response = model.generate_content(f"{ctx}\n\nProblema: {prompt}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    # Si el primer nombre falla, intentamos con el alternativo internamente
                    try:
                        alt_model = genai.GenerativeModel("models/gemini-1.5-flash")
                        response = alt_model.generate_content(f"{ctx}\n\nProblema: {prompt}")
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except:
                        st.error(f"Error de conexión: {e}")

    # Botón lateral para salir
    if st.sidebar.button("Finalizar Ticket"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.rerun()
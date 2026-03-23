import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

import auth_styles
import chat_styles

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")

api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Inicialización del modelo
if "model_name" not in st.session_state:
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.session_state.model_name = next((m for m in modelos if "flash" in m), modelos[0])
    except:
        st.session_state.model_name = "gemini-1.5-flash"

model = genai.GenerativeModel(st.session_state.model_name)

if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

try: logo_img = Image.open("logo.png")
except: logo_img = None

# --- 2. NAVEGACIÓN ---

if st.session_state.user_data is None:
    auth_styles.aplicar_auth()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, use_container_width=True)
        st.markdown("<h1 style='text-align:center; color:#0E3255;'>CoreDesk</h1>", unsafe_allow_html=True)
        with st.form("login"):
            nombre = st.text_input("Nombre Completo:")
            empresa = st.text_input("Empresa:")
            correo = st.text_input("Correo:")
            if st.form_submit_button("INICIAR SOPORTE"):
                if nombre and empresa and correo:
                    st.session_state.user_data = {"nombre": nombre, "empresa": empresa, "inicio": time.time()}
                    st.rerun()
                else: st.error("Rellena todos los campos.")

else:
    chat_styles.aplicar_chat()
    
    # Header Simple
    col_logo, col_timer = st.columns([8, 1])
    with col_logo:
        if logo_img: st.image(logo_img, width=120)
    with col_timer:
        t_min = int((time.time() - st.session_state.user_data['inicio']) / 60)
        st.write(f"⏱️ {t_min} min")

    # Tarjeta Usuario
    st.markdown(f"""
        <div class="user-card-pro">
            👤 <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Historial de Chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="🤖" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    # Chat Input Estándar (Sin botones que lo bloqueen)
    if prompt := st.chat_input("¿Cuál es el problema técnico hoy?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Respuesta de la IA
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    system_prompt = f"""
                    Eres el experto de Soporte Técnico de CoreDesk. Ayudas a {st.session_state.user_data['nombre']} de {st.session_state.user_data['empresa']}.
                    Responde con pasos numerados, usa negritas y sé muy específico.
                    Pregunta al final: "¿Te funcionó la información que te di?"
                    """
                    response = model.generate_content(f"{system_prompt}\n\nProblema: {prompt}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error de IA: {e}")
        st.rerun()
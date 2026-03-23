import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

import auth_styles
import chat_styles

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")

# Setup de IA - Fix para evitar error 404
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Usamos el identificador directo que es más estable
model = genai.GenerativeModel("gemini-1.5-flash")

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
    
    # Header con Logo y Contador
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

    # Chat Input
    if prompt := st.chat_input("¿Cuál es el problema técnico hoy?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Respuesta de la IA con Prompt Procedimental para Novatos
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    system_prompt = f"""
                    Eres el experto de Soporte de CoreDesk. Ayudas a {st.session_state.user_data['nombre']}.
                    
                    REGLAS:
                    1. Tono EXTREMADAMENTE amable y paciente (como para alguien que no sabe nada de PC).
                    2. Explica cada paso detalladamente. Ejemplo: 'Abre la carpeta naranja abajo en la barra' o 'Presiona la tecla Ctrl y la R al mismo tiempo'.
                    3. Usa pasos numerados y negritas.
                    4. Pregunta al final: "¿Te funcionó la información que te di?"
                    """
                    # Llamada directa
                    response = model.generate_content(f"{system_prompt}\n\nProblema: {prompt}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error de conexión con la IA: {e}")
        st.rerun()
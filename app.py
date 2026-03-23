import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

import auth_styles
import chat_styles

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", layout="wide")

api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

try: logo_img = Image.open("logo.png")
except: logo_img = None

# --- NAVEGACIÓN ---
if st.session_state.user_data is None:
    auth_styles.aplicar_auth()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, use_container_width=True)
        st.markdown("<h1 style='text-align:center; color:#0E3255;'>CoreDesk</h1>", unsafe_allow_html=True)
        with st.form("login"):
            nombre = st.text_input("Nombre:")
            empresa = st.text_input("Empresa:")
            correo = st.text_input("Correo:")
            if st.form_submit_button("INICIAR SOPORTE"):
                if nombre and empresa and correo:
                    st.session_state.user_data = {"nombre": nombre, "empresa": empresa, "inicio": time.time()}
                    st.rerun()

else:
    chat_styles.aplicar_chat()
    
    # Header
    col_logo, col_timer = st.columns([8, 1])
    with col_logo:
        if logo_img: st.image(logo_img, width=120)
    with col_timer:
        t_min = int((time.time() - st.session_state.user_data['inicio']) / 60)
        st.write(f"⏱️ {t_min} min")

    # Tarjeta Usuario
    st.markdown(f"""<div class="user-card-pro">👤 <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}</div>""", unsafe_allow_html=True)

    # Historial
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="🤖" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    # Chat Input
    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        # 1. Mostrar mensaje del usuario inmediatamente
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # 2. Generar respuesta
        with st.chat_message("assistant", avatar="🤖"):
            try:
                # Prompt amigable para novatos
                ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}. Explica como para alguien que no sabe nada de PC. Pregunta al final si funcionó."
                
                # LLAMADA DIRECTA (Sin session chat para evitar bloqueos)
                response = model.generate_content(f"{ctx}\n\nPregunta: {prompt}")
                respuesta_texto = response.text
                
                st.markdown(respuesta_texto)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
            except Exception as e:
                st.error(f"Error: {e}")
        
        # 3. Rerun manual para asegurar que se guarde el historial
        st.rerun()
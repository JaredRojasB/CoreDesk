import streamlit as st
import google.generativeai as genai
import os
import time
from PIL import Image

import global_styles
import auth_styles
import chat_styles

# --- SETUP ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")
global_styles.aplicar_globales()

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
            if st.form_submit_button("INICIAR"):
                if nombre and empresa and "@" in correo:
                    st.session_state.user_data = {"nombre": nombre, "empresa": empresa, "inicio": time.time()}
                    st.rerun()
                else: st.error("Datos incompletos")
else:
    chat_styles.aplicar_chat()
    
    # Header
    st.markdown(f"""
        <div class="header-fixed">
            <img src="https://raw.githubusercontent.com/tu-usuario/tu-repo/main/logo.png" class="logo-chat" style="height:50px;"> 
            <div style="color:#6c757d;">⏱️ Activo: {int((time.time()-st.session_state.user_data['inicio'])/60)} min</div>
        </div>
    """, unsafe_allow_html=True)

    # Tarjeta Usuario
    st.markdown(f"""
        <div style="background:white; padding:15px; border-radius:10px; border-left:5px solid #0E3255; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
            👤 <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}
        </div>
    """, unsafe_allow_html=True)

    # Chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # Botón + (Clip) flotando sobre la barra
    with st.popover("➕"):
        st.button("📷 Imagen", disabled=True)

    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("CoreDesk AI analizando..."):
                ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}. Sé procedimental (Win+R, etc)."
                res = model.start_chat(history=[]).send_message(f"{ctx}\n{prompt}").text
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})

    # BOTÓN X FLOTANTE (HTML Real)
    # Al dar clic, el sistema detecta el cambio de URL o puedes usar un botón oculto
    st.markdown('<a href="/" target="_self" id="finalizar-link">×</a>', unsafe_allow_html=True)
    
    # Si quieres que realmente borre sesión al dar clic:
    if st.button("invisible_exit", key="exit", help="Finalizar"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.rerun()
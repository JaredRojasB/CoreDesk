import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

import auth_styles
import chat_styles

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", layout="wide")

# IA Setup - Usando el modelo estándar más estable
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

# Logo
try: logo_img = Image.open("logo.png")
except: logo_img = None

# --- NAVEGACIÓN ---
if st.session_state.user_data is None:
    auth_styles.aplicar_auth()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, width=250)
        st.markdown("<h1 style='text-align:center; color:#0E3255;'>CoreDesk</h1>", unsafe_allow_html=True)
        with st.form("login"):
            n = st.text_input("Nombre:")
            e = st.text_input("Empresa:")
            c = st.text_input("Correo:")
            if st.form_submit_button("INICIAR SOPORTE"):
                if n and e and "@" in c:
                    st.session_state.user_data = {"nombre": n, "empresa": e, "inicio": time.time()}
                    st.rerun()
else:
    chat_styles.aplicar_chat()
    
    # 1. HEADER Y CONTADOR
    t_min = int((time.time() - st.session_state.user_data['inicio']) / 60)
    col_h1, col_h2 = st.columns([8, 1])
    with col_h1:
        if logo_img: st.image(logo_img, width=120) # Logo legible
    with col_h2:
        st.markdown(f"⏱️ **{t_min} min**")

    # 2. TARJETA DE USUARIO
    st.markdown(f"""
        <div class="user-card">
            👤 <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}
        </div>
    """, unsafe_allow_html=True)

    # 3. BIENVENIDA ÚNICA (Lógica simple)
    if not st.session_state.messages:
        bienvenida = f"Hola **{st.session_state.user_data['nombre']}**, soy tu Asistente CoreDesk. ¿Cuál es el problema en **{st.session_state.user_data['empresa']}**?"
        st.session_state.messages.append({"role": "assistant", "content": bienvenida})

    # 4. HISTORIAL DE CHAT
    for m in st.session_state.messages:
        # Aquí el avatar 'assistant' cargará un robot con fondo naranja si lo pones así
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # 5. INPUT CON EL "+" AL LADO (Estructura de columnas estable)
    col_plus, col_input = st.columns([1, 15])
    with col_plus:
        with st.popover("➕"):
            st.button("📷 Imagen", disabled=True)
    
    with col_input:
        if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Respuesta de la IA
            with st.chat_message("assistant"):
                with st.spinner("CoreDesk AI analizando..."):
                    try:
                        ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}."
                        res = model.start_chat(history=[]).send_message(f"{ctx}\n{prompt}").text
                        st.markdown(res)
                        st.session_state.messages.append({"role": "assistant", "content": res})
                    except Exception as e:
                        st.error("Error de conexión con la IA. Intenta de nuevo.")
            st.rerun()

    # 6. BOTÓN X FLOTANTE (Link real)
    st.markdown('<a href="/" target="_self" class="floating-x">×</a>', unsafe_allow_html=True)
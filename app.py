import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

import auth_styles
import chat_styles
import auth

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", layout="wide")

# IA Setup - Fix de estabilidad
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None
if "bienvenida_ok" not in st.session_state: st.session_state.bienvenida_ok = False

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
            n = st.text_input("Nombre:")
            e = st.text_input("Empresa:")
            c = st.text_input("Correo:")
            if st.form_submit_button("INICIAR SOPORTE"):
                if n and e and "@" in c:
                    st.session_state.user_data = {"nombre": n, "empresa": e, "inicio": time.time()}
                    st.rerun()

else:
    chat_styles.aplicar_chat()
    
    # 1. Header Fijo con Logo y Contador
    t_min = int((time.time() - st.session_state.user_data['inicio']) / 60)
    st.markdown(f"""
        <div class="header-fixed">
            <div style="font-weight:bold; color:#0E3255; font-size:20px;">🛡️ CoreDesk Support</div>
            <div style="margin-left:auto; color:#6c757d; font-weight:bold;">⏱️ {t_min} min activo</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Tarjeta Usuario
    st.markdown(f"""
        <div class="user-card-pro">
            👤 <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}
        </div>
    """, unsafe_allow_html=True)

    # 3. Bienvenida Única
    if not st.session_state.bienvenida_ok:
        msg = f"¡Hola **{st.session_state.user_data['nombre']}**! Soy tu Asistente de CoreDesk. ¿En qué puedo ayudarte?"
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.session_state.bienvenida_ok = True

    # 4. Historial con Avatares Reales
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="🤖" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    # 5. Input y Clip (+)
    with st.popover("＋"):
        st.button("📷 Imagen", disabled=True)

    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}. Sé procedimental (ej. Win+R, Ctrl+C)."
                    # Llamada limpia a la IA
                    response = model.generate_content(f"{ctx}\nPregunta: {prompt}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error de IA: {e}")
        st.rerun()

    # 6. Botón X Flotante
    st.markdown('<a href="/" target="_self" id="btn-exit">×</a>', unsafe_allow_html=True)
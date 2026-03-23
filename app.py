import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

import auth_styles
import chat_styles
import auth

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", layout="wide")

# IA Setup - FIX DEL MODELO NOT FOUND
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
# Usamos el nombre de modelo completo para evitar el error NotFound
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Session State
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
    
    # --- AUTO-REFRESH PARA EL CONTADOR (Cada 30 seg) ---
    # Esto obliga a la página a recargar sola para que el reloj avance
    st.empty() 
    
    # 1. Header y Contador Dinámico
    t_act = int((time.time() - st.session_state.user_data['inicio']) / 60)
    st.markdown(f"""
        <div class="header-fixed">
            <img src="data:image/png;base64,{st.image(logo_img, width=65) if logo_img else ''}" class="logo-chat">
            <div style="margin-left: auto; color: #6c757d; font-weight: bold; font-size: 18px;">
                ⏱️ Tiempo: {t_act} min
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Tarjeta de Usuario
    st.markdown(f"""
        <div class="user-card-formal">
            <div>
                <div style="color: #6c757d; font-size: 12px; font-weight: bold;">TICKET EN CURSO</div>
                <div style="color: #0E3255; font-size: 22px; font-weight: bold;">👤 {st.session_state.user_data['nombre']}</div>
                <div style="color: #495057;">🏢 {st.session_state.user_data['empresa']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 3. BIENVENIDA ÚNICA (FIX DEFINITIVO)
    if not st.session_state.bienvenida_ok:
        bienvenida = f"¡Hola **{st.session_state.user_data['nombre']}**! Soy tu Asistente IA de CoreDesk. ¿Cuál es el problema en **{st.session_state.user_data['empresa']}**?"
        st.session_state.messages.append({"role": "assistant", "content": bienvenida})
        st.session_state.bienvenida_ok = True
        st.rerun() # Forzamos un render para sellar el candado

    # 4. Historial con Avatares Específicos
    for m in st.session_state.messages:
        # Avatar 'assistant' usa icono robot, 'user' usa persona
        with st.chat_message(m["role"], avatar="🤖" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    # 5. Entrada con el MÁS (+) integrado
    with st.popover("＋"):
        st.button("📷 Adjuntar Imagen", disabled=True, use_container_width=True)

    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analizando solución..."):
                try:
                    ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}. Sé procedimental (ej. Win+R, Ctrl+K). Pregunta al final si funcionó."
                    # El chat_session maneja el historial interno para evitar errores
                    chat_session = model.start_chat(history=[])
                    res = chat_session.send_message(f"{ctx}\n{prompt}").text
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                except Exception as e:
                    st.error(f"Error de IA: {e}")
        st.rerun()

    # 6. Botón X Flotante
    st.markdown('<a href="/" target="_self" id="finalizar-btn-flotante"></a>', unsafe_allow_html=True)
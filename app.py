import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

import auth_styles
import chat_styles # Verifica que el archivo se llame así
import auth

st.set_page_config(page_title="CoreDesk Support", layout="wide")

api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None
if "bienvenida_dada" not in st.session_state: st.session_state.bienvenida_dada = False

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
                if nombre and empresa and "@" in correo:
                    st.session_state.user_data = {"nombre": nombre, "empresa": empresa, "inicio": time.time()}
                    st.rerun()

else:
    # --- AQUÍ LLAMAMOS A LA FUNCIÓN DEL OTRO ARCHIVO ---
    chat_styles.aplicar_chat() 
    
    # 1. Header con Logo (Izquierda) y Contador (Derecha)
    t_min = int((time.time() - st.session_state.user_data['inicio']) / 60)
    st.markdown(f"""
        <div class="header-fixed">
            <img src="https://raw.githubusercontent.com/tu-usuario/tu-repo/main/logo.png" class="logo-chat" style="height:50px;"> 
            <div style="margin-left: auto; color: #6c757d; font-weight: bold;">⏱️ Activo: {t_min} min</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Tarjeta de Usuario Formal
    st.markdown(f"""
        <div class="user-card-formal">
            <div>
                <div style="color: #6c757d; font-size: 12px;">SOPORTE ACTIVO</div>
                <div style="color: #0E3255; font-size: 18px; font-weight: bold;">👤 {st.session_state.user_data['nombre']}</div>
                <div style="color: #495057;">🏢 {st.session_state.user_data['empresa']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 3. Bienvenida Única (Candado para que no se repita)
    if not st.session_state.bienvenida_dada:
        msg_bienvenida = f"¡Hola **{st.session_state.user_data['nombre']}**! Soy tu Asistente IA de CoreDesk. ¿Cuál es el problema en **{st.session_state.user_data['empresa']}**?"
        st.session_state.messages.append({"role": "assistant", "content": msg_bienvenida})
        st.session_state.bienvenida_dada = True

    # 4. Historial con Avatares (Robot y Usuario Azul)
    for m in st.session_state.messages:
        # Forzamos avatar de emoji para evitar el smart_toy naranja
        av = "🤖" if m["role"] == "assistant" else "👤"
        with st.chat_message(m["role"], avatar=av):
            st.markdown(m["content"])

    # 5. Entrada con Clip integrado (Popover)
    with st.popover("📎"):
        st.button("📷 Subir Imagen", disabled=True)

    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
                usr = st.session_state.user_data['nombre']
                # Prompt procedimental (Win+R, Ctrl+K, etc)
                ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {usr}. Sé extremadamente específico con rutas y comandos de teclado. Pregunta al final si funcionó."
                res = model.start_chat(history=[]).send_message(f"{ctx}\n{prompt}").text
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
        st.rerun()

    # 6. Botón X Roja Flotante
    st.markdown('<a href="/" target="_self" id="finalizar-btn-flotante" title="Finalizar Chat"></a>', unsafe_allow_html=True)
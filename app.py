import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

import auth_styles
import chat_styles 
import auth

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", layout="wide", page_icon="🛡️")

# IA Setup
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Session State inicial
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None
if "bienvenida_dada" not in st.session_state: st.session_state.bienvenida_dada = False

# Carga de Logo
try:
    logo_img = Image.open("logo.png")
except:
    logo_img = None

# --- 2. NAVEGACIÓN ---

if st.session_state.user_data is None:
    # --- PANTALLA DE INICIO ---
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
                if nombre and empresa and "@" in correo:
                    st.session_state.user_data = {"nombre": nombre, "empresa": empresa, "inicio": time.time()}
                    st.rerun()
                else:
                    st.error("Por favor rellena todos los campos correctamente.")

else:
    # --- PANTALLA DE CHAT ACTIVA ---
    chat_styles.aplicar_chat() 
    
    # 1. Header Fijo con Logo y Contador
    t_min = int((time.time() - st.session_state.user_data['inicio']) / 60)
    
    # Usamos columnas de Streamlit dentro del header para que el logo se vea
    header_container = st.container()
    with header_container:
        col_logo, col_espacio, col_time = st.columns([1, 4, 1])
        with col_logo:
            if logo_img: st.image(logo_img, width=50) # Logo pequeño arriba a la izquierda
        with col_time:
            st.markdown(f"<div style='text-align:right; color:#6c757d; font-weight:bold; margin-top:10px;'>⏱️ {t_min} min</div>", unsafe_allow_html=True)

    # 2. Tarjeta de Usuario Formal
    st.markdown(f"""
        <div class="user-card-formal">
            <div>
                <div style="color: #6c757d; font-size: 11px; font-weight: bold; letter-spacing: 1px;">INFORMACIÓN DEL TICKET</div>
                <div style="color: #0E3255; font-size: 19px; font-weight: 800; margin-top: 5px;">👤 {st.session_state.user_data['nombre']}</div>
                <div style="color: #495057; font-size: 14px;">🏢 {st.session_state.user_data['empresa']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 3. Bienvenida Única
    if not st.session_state.bienvenida_dada:
        with st.chat_message("assistant", avatar="🤖"):
            msg_bienvenida = f"¡Hola **{st.session_state.user_data['nombre']}**! Soy tu Asistente IA de CoreDesk. ¿Cuál es el problema en **{st.session_state.user_data['empresa']}**?"
            st.markdown(msg_bienvenida)
            st.session_state.messages.append({"role": "assistant", "content": msg_bienvenida})
        st.session_state.bienvenida_dada = True # Candado puesto

    # 4. Historial con Avatares Limpios
    for m in st.session_state.messages:
        av = "🤖" if m["role"] == "assistant" else "👤"
        with st.chat_message(m["role"], avatar=av):
            st.markdown(m["content"])

    # 5. Entrada con Botón "+" (Clip/Popover)
    # Lo colocamos antes del input para que el CSS lo posicione a la izquierda
    with st.popover("➕"):
        st.markdown("**Opciones de adjunto**")
        st.button("📷 Subir Imagen", use_container_width=True, disabled=True)

    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): 
            st.markdown(prompt)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analizando solución..."):
                usr = st.session_state.user_data['nombre']
                ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {usr}. Sé extremadamente específico con rutas de Windows y comandos de teclado (ej. Win+R, Ctrl+C). Pregunta al final si funcionó."
                res = model.start_chat(history=[]).send_message(f"{ctx}\n{prompt}").text
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
        st.rerun()

    # 6. Botón X Roja Flotante (Llamando al ID de chat_styles)
    st.markdown('<a href="/" target="_self" id="finalizar-btn-flotante" title="Finalizar Chat"></a>', unsafe_allow_html=True)
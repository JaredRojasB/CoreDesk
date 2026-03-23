import streamlit as st
import google.generativeai as genai
import os
import time
from PIL import Image

# IMPORTAMOS TUS 3 ARCHIVOS CSS MODULARES
import styles      # Global e Inicio
import chat_styles # Exclusivo Chat
import auth        # Lógica de Login

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")
styles.aplicar_estilos_globales() # Pintura Global (fondo blanco)

# IA Setup
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

# Carga de Logo
try:
    # Asegúrate de que el archivo se llame exactamente 'logo.png'
    logo_img = Image.open("logo.png")
except:
    logo_img = None

# --- 2. LÓGICA DE NAVEGACIÓN (Control visual) ---

# CASO A: Pantalla de Registro
if st.session_state.user_data is None:
    styles.aplicar_estilos_inicio() # Aplicamos CSS de Inicio
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, use_container_width=True)
        st.markdown("<p class='core-title-main'>CoreDesk</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6c757d; margin-bottom: 20px;'>Sistema de Soporte Técnico Inteligente</p>", unsafe_allow_html=True)
        auth.mostrar_registro()

# CASO B: Pantalla de Chat Activa
else:
    chat_styles.aplicar_estilos_chat() # ¡BUM! Aplicamos CSS Exclusivo de Chat
    
    # 1. Header Fijo (Controlado por CSS de chat)
    st.markdown('<div class="header-fixed">', unsafe_allow_html=True)
    col_h1, col_h2, col_h3 = st.columns([1, 6, 2])
    with col_h1:
        # LOGO LEGIBLE (Tamaño controlado por CSS a 120px)
        if logo_img: st.image(logo_img, use_container_width=True)
    with col_h3:
        # BOTÓN FINALIZAR ROJO (Controlado por CSS a ROJO)
        if st.button("FINALIZAR", key="exit_chat"):
            with st.spinner("Cerrando ticket de forma segura..."):
                time.sleep(0.5)
                st.session_state.user_data = None
                st.session_state.messages = []
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Info Usuario (Sutil, integrada arriba)
    st.markdown(f"<p class='user-tag-chat'>Soporte técnico activo para: <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}</p>", unsafe_allow_html=True)
    st.divider()

    # 3. Historial de Chat (Con identidad de burbujas)
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): 
            st.markdown(m["content"])

    # 4. Barra de Chat FIJA Abajo (Controlado por CSS)
    col_clip, col_txt = st.columns([1, 15])
    with col_clip:
        # Usamos popover para el menú desplegable del clip
        menu_archivos = st.popover("📎", help="Adjuntar archivos")
        with menu_archivos:
            st.write("Selecciona archivo:")
            st.button("📷 Subir Imagen", disabled=True) # Botón inactivo por ahora

    with col_txt:
        if prompt := st.chat_input("Escribe tu duda técnica aquí...", key="chat_input"):
            # Lógica de IA... (sin cambios)
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("CoreDesk AI analizando..."):
                    try:
                        ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}."
                        chat = model.start_chat(history=[])
                        res = chat.send_message(f"{ctx}\n{prompt}").text
                        st.markdown(res)
                        st.session_state.messages.append({"role": "assistant", "content": res})
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
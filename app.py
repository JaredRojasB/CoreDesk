import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from datetime import datetime
from PIL import Image

# IMPORTAMOS TUS MÓDULOS DE ESTILO Y AUTH
import styles
import auth

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support AI", page_icon="🛡️", layout="wide")
styles.aplicar_estilos() # Aplicamos la pintura GLOBAL

# --- IA SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Gestión de Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

# --- CARGA DE LOGO (Una sola vez para uso global) ---
# Intentamos cargar la imagen una sola vez al inicio para ahorrar recursos
# Asegúrate de que el nombre sea idéntico al de tu explorador de archivos
logo_path = "logo.png"
logo_available = False
try:
    logo_img = Image.open(logo_path)
    logo_available = True
except:
    # Si no la encuentra, logo_available se mantiene False y usaremos el emoji
    pass

# --- LÓGICA DE NAVEGACIÓN ---

# Caso A: Pantalla de Registro (Logo GRANDE y CENTRADO)
if st.session_state.user_data is None:
    # Banner Principal (Solo visible en registro)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        if logo_available:
            # Mostramos el logo grande aquí, como banner
            st.image(logo_img, use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center;'>🛡️</h1>", unsafe_allow_html=True)
    st.markdown("<p class='core-title' style='text-align: center;'>CoreDesk</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6c757d;'>Sistema de Soporte Técnico Inteligente</p>", unsafe_allow_html=True)
    
    # Mostramos el formulario de auth (este ya está limpio en su propio archivo)
    auth.mostrar_registro()

# Caso B: Pantalla de Chat Activo (Logo PEQUEÑO en esquina)
else:
    # BARRA SUPERIOR DEL CHAT
    # Separamos en 3 columnas: Usuario, Logo Pequeño, Botón Finalizar
    c1, c2, c3 = st.columns([10, 2, 2]) # Ajustamos anchos para balancear
    
    with c1:
        st.write(f"Usuario: **{st.session_state.user_data['nombre']}** | {st.session_state.user_data['empresa']}")
    
    with c2:
        # AQUÍ PONEMOS EL LOGO PEQUEÑO Y RESPONSIVO
        if logo_available:
            # Creamos un contenedor HTML para el CSS responsivo
            st.markdown('<div class="chat-logo-container">', unsafe_allow_html=True)
            st.image(logo_img, use_container_width=True) # El CSS controlará el max-width
            st.markdown('</div>', unsafe_allow_html=True)
    
    with c3:
        st.markdown('<div class="btn-finalizar">', unsafe_allow_html=True)
        if st.button("FINALIZAR"):
            st.session_state.user_data = None
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---") # Línea divisoria

    # HISTORIAL DE MENSAJES
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): 
            st.markdown(m["content"])

    # ENTRADA DE CHAT CON CLIP
    col_clip, col_txt = st.columns([1, 15])
    with col_clip:
        with st.popover("📎"):
            st.write("Adjuntar:")
            st.button("📷 Imagen del problema (Hardware)", disabled=True)
    
    with col_txt:
        if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): 
                st.markdown(prompt)
            
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
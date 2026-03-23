import streamlit as st
import google.generativeai as genai
import os
import time
from PIL import Image
import styles
import auth

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")
styles.aplicar_estilos()

# IA Setup
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

# Carga de Logo (logo.png)
try:
    logo_img = Image.open("logo.png")
except:
    logo_img = None

# --- 2. LÓGICA DE NAVEGACIÓN ---
if st.session_state.user_data is None:
    # PANTALLA DE REGISTRO
    # Definimos las columnas correctamente aquí para evitar el NameError
    col_inic1, col_inic2, col_inic3 = st.columns([1, 2, 1])
    with col_inic2:
        if logo_img: 
            st.image(logo_img, use_container_width=True)
        st.markdown("<h1 style='text-align:center; color:#0E3255;'>CoreDesk</h1>", unsafe_allow_html=True)
        auth.mostrar_registro()

else:
    # --- PANTALLA DE CHAT ACTIVA ---
    
    # Header: Logo (Izq) | Botón Finalizar (Der)
    head_left, head_spacer, head_right = st.columns([1, 6, 1])
    
    with head_left:
        if logo_img: 
            st.image(logo_img, width=80) # Logo pequeño arriba a la izquierda
    
    with head_right:
        # Botón FINALIZAR (Saldrá rojo por el CSS en styles.py)
        if st.button("FINALIZAR", key="btn_exit"):
            st.session_state.user_data = None
            st.session_state.messages = []
            st.rerun()

    # Info del usuario (Limpio y sutil)
    st.markdown(f"👤 **{st.session_state.user_data['nombre']}** | 🏢 **{st.session_state.user_data['empresa']}**")
    st.divider()

    # Historial de Chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): 
            st.markdown(m["content"])

    # Entrada de Chat con el '+' integrado visualmente
    # Usamos columnas pequeñas para que el '+' parezca parte de la barra
    chat_col_plus, chat_col_input = st.columns([1, 20])
    
    with chat_col_plus:
        # El botón de adjuntar como un símbolo de más
        with st.popover("➕"):
            st.write("Adjuntar Evidencia")
            st.button("📷 Subir Imagen", disabled=True)
    
    with chat_col_input:
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
                        st.error(f"Error: {e}")
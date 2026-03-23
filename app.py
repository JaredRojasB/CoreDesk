import streamlit as st
import google.generativeai as genai
import os
import time
from PIL import Image
import styles
import auth

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")
styles.aplicar_estilos()

# IA Setup
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

# Carga de Logo
try:
    logo_img = Image.open("logo.png")
except:
    logo_img = None

# --- NAVEGACIÓN ---
if st.session_state.user_data is None:
    # Pantalla de Bienvenida (Logo Grande)
    c1, c2, c3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, width=200)
        st.markdown("<h1 style='text-align:center; color:#0E3255;'>CoreDesk</h1>", unsafe_allow_html=True)
        auth.mostrar_registro()

else:
    # --- INTERFAZ DE CHAT ---
    
    # 1. HEADER (Logo Izq | Botón Der)
    head_col1, head_col2 = st.columns([8, 1])
    with head_col1:
        if logo_img: st.image(logo_img, width=80)
    with head_col2:
        if st.button("FINALIZAR"):
            st.session_state.user_data = None
            st.session_state.messages = []
            st.rerun()

    # 2. INFO USUARIO (Limpio)
    st.caption(f"👤 {st.session_state.user_data['nombre']} | 🏢 {st.session_state.user_data['empresa']}")
    st.divider()

    # 3. HISTORIAL
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # 4. ENTRADA DE CHAT CON '+' INTEGRADO
    # Ponemos el popover y el input en la misma fila
    chat_col1, chat_col2 = st.columns([1, 15])
    with chat_col1:
        with st.popover("➕"):
            st.button("📷 Imagen", disabled=True)
    
    with chat_col2:
        if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Analizando..."):
                    ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}."
                    res = model.start_chat(history=[]).send_message(f"{ctx}\n{prompt}").text
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
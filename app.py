import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import styles
import auth

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support AI", page_icon="🛡️", layout="wide")
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
    # Pantalla de Inicio (Logo Grande)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        if logo_img: st.image(logo_img, use_container_width=True)
    st.markdown("<p class='core-title'>CoreDesk</p>", unsafe_allow_html=True)
    auth.mostrar_registro()

else:
    # --- PANTALLA DE CHAT ---
    
    # 1. Header: Logo (Izq) y Botón Finalizar (Der)
    col_head_1, col_head_2 = st.columns([8, 1])
    with col_head_1:
        if logo_img:
            st.markdown('<div class="chat-logo-container">', unsafe_allow_html=True)
            st.image(logo_img)
            st.markdown('</div>', unsafe_allow_html=True)
    with col_head_2:
        if st.button("FINALIZAR", use_container_width=True):
            st.session_state.user_data = None
            st.session_state.messages = []
            st.rerun()

    # 2. Apartado de Usuario (Separado del logo)
    st.markdown(f"""
        <div class="user-info-box">
            👤 Usuario: {st.session_state.user_data['nombre']} | 🏢 Empresa: {st.session_state.user_data['empresa']}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. Historial de Chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # 4. Input con botón '+' integrado
    st.markdown('<div class="plus-button-container">', unsafe_allow_html=True)
    with st.popover("➕"):
        st.write("Adjuntar Evidencia")
        st.button("📷 Subir Imagen", disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("CoreDesk AI analizando..."):
                ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}."
                res = model.start_chat(history=[]).send_message(f"{ctx}\n{prompt}").text
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
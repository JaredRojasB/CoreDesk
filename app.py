import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from datetime import datetime
from PIL import Image

# IMPORTAMOS TUS NUEVOS ARCHIVOS
import styles
import auth

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support AI", page_icon="🛡️", layout="wide")
styles.aplicar_estilos() # Aplicamos la pintura

# --- IA SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

# --- BANNER (Siempre visible) ---
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    try:
        st.image(Image.open("Logo CoreDesk.png"), use_container_width=True)
    except: st.markdown("<h1 style='text-align: center;'>🛡️</h1>", unsafe_allow_html=True)
st.markdown("<p class='core-title' style='text-align: center;'>CoreDesk</p>", unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if st.session_state.user_data is None:
    auth.mostrar_registro()
else:
    # CABECERA DEL CHAT
    c1, c2 = st.columns([6, 1])
    with c1:
        st.write(f"Usuario: **{st.session_state.user_data['nombre']}**")
    with c2:
        st.markdown('<div class="btn-finalizar">', unsafe_allow_html=True)
        if st.button("FINALIZAR"):
            st.session_state.user_data = None
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # HISTORIAL
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # ENTRADA DE CHAT CON CLIP
    col_clip, col_txt = st.columns([1, 15])
    with col_clip:
        with st.popover("📎"):
            st.button("📷 Imagen del problema", disabled=True)
    
    with col_txt:
        if prompt := st.chat_input("Escribe tu duda técnica..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Analizando..."):
                    ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}."
                    res = model.start_chat(history=[]).send_message(f"{ctx}\n{prompt}").text
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
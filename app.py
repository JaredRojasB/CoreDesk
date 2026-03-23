import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import re
import time
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support AI", page_icon="🛡️", layout="centered")

# --- 2. CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .stButton>button {
        border-radius: 10px; background-color: #0E3255; color: white;
        font-weight: bold; width: 100%; height: 3.5em;
    }
    .stSpinner > div { border-top-color: #0E3255 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INICIALIZACIÓN ---
load_dotenv()
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None
if "cargando" not in st.session_state: st.session_state.cargando = False

def es_correo_valido(correo):
    return re.match(r'^[a-zA-Z0-9_.+-]+@(gmail\.com|outlook\.com|hotmail\.com)$', correo)

# --- 4. CABECERA ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image(Image.open("Logo CoreDesk.png"), use_container_width=True)
    except:
        st.markdown("<h1 style='text-align: center;'>🛡️</h1>", unsafe_allow_html=True)

# --- 5. LÓGICA DE REGISTRO ---
if st.session_state.user_data is None:
    st.markdown("<h1 style='text-align: center; color: #0E3255;'>CoreDesk</h1>", unsafe_allow_html=True)
    st.subheader("📝 Apertura de Ticket")
    
    nombre = st.text_input("Nombre Completo:")
    empresa = st.text_input("Empresa / Departamento:")
    correo = st.text_input("Correo Electrónico:")

    if st.button("INICIAR SOPORTE"):
        st.session_state.cargando = True

    if st.session_state.cargando:
        with st.spinner("Sincronizando con los servidores de CoreDesk..."):
            time.sleep(1.5) 
            
            if not nombre or not empresa or not correo:
                st.error("❌ Por favor, completa todos los campos del ticket.")
                st.session_state.cargando = False 
            elif not es_correo_valido(correo):
                st.error("❌ El dominio del correo no es válido (Usa Gmail, Outlook o Hotmail).")
                st.session_state.cargando = False 
            else:
                st.session_state.user_data = {"nombre": nombre, "empresa": empresa, "correo": correo}
                st.session_state.cargando = False
                st.success("✅ Acceso autorizado.")
                st.rerun()

else:
    # --- INTERFAZ DE CHAT ---
    st.markdown(f"**Ticket abierto por:** {st.session_state.user_data['nombre']}")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando base de conocimientos AI..."):
                try:
                    ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}."
                    res = model.start_chat(history=[]).send_message(f"{ctx}\nProblema: {prompt}").text
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                except Exception as e:
                    st.error(f"Error de red: {e}")

    with st.sidebar:
        if st.button("🔴 FINALIZAR"):
            st.session_state.user_data = None
            st.session_state.messages = []
            st.rerun()
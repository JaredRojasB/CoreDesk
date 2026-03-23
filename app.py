import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", layout="wide")

# Logo
try: logo_img = Image.open("logo.png")
except: logo_img = None

# --- 2. EL CSS MÁS AGRESIVO POSIBLE ---
# Aquí atacamos a CUALQUIER círculo que tenga un emoji adentro
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    
    /* 1. NARANJA PARA EL ASISTENTE (BOT) */
    /* Buscamos el contenedor que tiene el emoji de robot */
    div[data-testid="stChatMessageAssistant"] div[data-testid="stChatMessageAvatar"] {
        background-color: #FF8C00 !important;
        border: 2px solid #FF8C00 !important;
    }
    /* Atacamos todas las capas internas posibles del bot */
    div[data-testid="stChatMessageAssistant"] [class*="st-emotion-cache"] {
        background-color: #FF8C00 !important;
        border-radius: 50% !important;
    }

    /* 2. AZUL PARA EL USUARIO */
    div[data-testid="stChatMessageUser"] div[data-testid="stChatMessageAvatar"] {
        background-color: #0E3255 !important;
        border: 2px solid #0E3255 !important;
    }
    div[data-testid="stChatMessageUser"] [class*="st-emotion-cache"] {
        background-color: #0E3255 !important;
        border-radius: 50% !important;
    }

    /* Limpieza y Botón Rojo */
    div[data-testid="stHeader"], div[data-testid="stSidebarNav"], [data-testid="stIconMaterial"] { 
        display: none !important; 
    }
    
    div.stButton > button[key="finalizar-btn"] {
        position: fixed !important; bottom: 30px !important; left: 30px !important;
        background-color: #FF4B4B !important; color: white !important;
        border-radius: 50px !important; width: 160px !important; z-index: 1000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE IA ---
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

if "model" not in st.session_state:
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        nombre = next((m for m in modelos if "flash" in m), modelos[0])
        st.session_state.model = genai.GenerativeModel(nombre)
    except Exception as e:
        st.error(f"Error IA: {e}"); st.stop()

if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None
if "bienvenida_ok" not in st.session_state: st.session_state.bienvenida_ok = False

# --- 4. INTERFAZ ---
if st.session_state.user_data is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, width=150)
        with st.form("login"):
            n = st.text_input("Nombre:")
            e = st.text_input("Empresa:")
            if st.form_submit_button("INGRESAR"):
                if n and e:
                    st.session_state.user_data = {"nombre": n, "empresa": e, "inicio": time.time()}
                    st.rerun()
else:
    # Header
    st.markdown('<div style="position:fixed;top:0;left:0;width:100%;height:70px;background:white;z-index:998;display:flex;align-items:center;padding:0 5%;border-bottom:1px solid #EEE;">', unsafe_allow_html=True)
    if logo_img: st.image(logo_img, width=100)
    st.markdown('</div><div style="margin-top:90px;"></div>', unsafe_allow_html=True)

    # Bienvenida
    if not st.session_state.bienvenida_ok:
        st.session_state.messages.append({"role": "assistant", "content": f"¡Hola **{st.session_state.user_data['nombre']}**! 👋 ¿Cómo va el soporte en **{st.session_state.user_data['empresa']}**?"})
        st.session_state.bienvenida_ok = True

    # Historial
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="🤖" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    # Input
    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            try:
                ctx = f"Eres experto CoreDesk ayudando a {st.session_state.user_data['nombre']}. Explica paso a paso. Pitidos 3 largos/2 cortos = RAM/Motherboard."
                res = st.session_state.model.generate_content(f"{ctx}\n\nProblema: {prompt}")
                st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
            except Exception as e: st.error(f"Error: {e}")
        st.rerun()

    if st.button("Finalizar Chat", key="finalizar-btn"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.session_state.bienvenida_ok = False
        st.rerun()
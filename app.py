import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")

# Logo
try: logo_img = Image.open("logo.png")
except: logo_img = None

# --- 2. INYECCIÓN DE ESTILOS CSS (RE-INGENIERÍA DE COLORES) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* Ocultar elementos nativos */
    div[data-testid="stHeader"], div[data-testid="stSidebarNav"] { display: none; }
    
    /* --- FUERZA BRUTA PARA COLORES DE ICONOS --- */
    
    /* 1. ASISTENTE (BOT) -> NARANJA CoreDesk */
    /* Seleccionamos el contenedor del avatar del asistente */
    [data-testid="stChatMessageAssistant"] div[data-testid="stChatMessageAvatar"] {
        background-color: #FF8C00 !important;
        color: white !important;
        border: 2px solid #FF8C00 !important;
    }
    /* Seleccionamos el círculo interno del avatar */
    [data-testid="stChatMessageAssistant"] .st-emotion-cache-1pxm8gg,
    [data-testid="stChatMessageAssistant"] .st-emotion-cache-p4m09v {
        background-color: #FF8C00 !important;
    }

    /* 2. USUARIO -> AZUL MARINO CoreDesk */
    [data-testid="stChatMessageUser"] div[data-testid="stChatMessageAvatar"] {
        background-color: #0E3255 !important;
        color: white !important;
        border: 2px solid #0E3255 !important;
    }
    [data-testid="stChatMessageUser"] .st-emotion-cache-1pxm8gg,
    [data-testid="stChatMessageUser"] .st-emotion-cache-p4m09v {
        background-color: #0E3255 !important;
    }

    /* Limpieza de basura visual */
    [data-testid="stIconMaterial"], span[data-testid="stWidgetLabel"] { 
        display: none !important; 
    }

    /* BOTÓN ROJO DE FINALIZAR FIJO */
    div.stButton > button[key="finalizar-btn"] {
        position: fixed !important;
        bottom: 30px !important;
        left: 30px !important;
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 50px !important;
        width: 160px !important;
        z-index: 1000 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE IA ---
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

if "model" not in st.session_state:
    try:
        modelos_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        nombre_modelo = next((m for m in modelos_disponibles if "flash" in m), modelos_disponibles[0])
        st.session_state.model = genai.GenerativeModel(nombre_modelo)
    except Exception as e:
        st.error(f"Error de conexión con la IA: {e}")
        st.stop()

# --- 4. GESTIÓN DE SESIÓN ---
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None
if "bienvenida_enviada" not in st.session_state: st.session_state.bienvenida_enviada = False

# --- 5. INTERFAZ ---
if st.session_state.user_data is None:
    # Pantalla Registro
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, width=150)
        st.markdown("<h1 style='color:#0E3255; text-align:center;'>CoreDesk</h1>", unsafe_allow_html=True)
        with st.form("registro"):
            n = st.text_input("Nombre:")
            e = st.text_input("Empresa:")
            if st.form_submit_button("INGRESAR"):
                if n and e:
                    st.session_state.user_data = {"nombre": n, "empresa": e, "inicio": time.time()}
                    st.rerun()
else:
    # Header y Chat
    st.markdown('<div style="position:fixed;top:0;left:0;width:100%;height:70px;background:white;z-index:999;display:flex;align-items:center;padding:0 5%;border-bottom:1px solid #EEE;">', unsafe_allow_html=True)
    if logo_img: st.image(logo_img, width=100)
    inicio_t = st.session_state.user_data.get('inicio', time.time())
    t_min = int((time.time() - inicio_t) / 60)
    st.markdown(f'<div style="margin-left:auto;color:#6c757d;font-weight:bold;">⏱️ {t_min} min activo</div>', unsafe_allow_html=True)
    st.markdown('</div><div style="margin-top:90px;"></div>', unsafe_allow_html=True)

    # Tarjeta Usuario
    st.markdown(f'<div style="background:white;padding:15px;border-radius:10px;border-left:5px solid #0E3255;box-shadow:0 2px 5px rgba(0,0,0,0.05);">👤 <b>{st.session_state.user_data["nombre"]}</b> | 🏢 {st.session_state.user_data["empresa"]}</div>', unsafe_allow_html=True)

    if not st.session_state.bienvenida_enviada:
        st.session_state.messages.append({"role": "assistant", "content": f"¡Hola **{st.session_state.user_data['nombre']}**! 👋 ¿Qué problema técnico presentas?"})
        st.session_state.bienvenida_enviada = True

    for m in st.session_state.messages:
        # ASIGNAMOS EL ROLE CORRECTO PARA EL CSS
        role_css = "assistant" if m["role"] == "assistant" else "user"
        with st.chat_message(m["role"], avatar="🤖" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    ctx = f"Eres experto CoreDesk ayudando a {st.session_state.user_data['nombre']}. Explica paso a paso. Si mencionan pitidos (3 largos, 2 cortos), explica que es error de RAM o Tarjeta Madre y cómo revisarlo amablemente."
                    res = st.session_state.model.generate_content(f"{ctx}\n\nProblema: {prompt}")
                    st.markdown(res.text)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                except Exception as e: st.error(f"Error: {e}")
        st.rerun()

    if st.button("Finalizar Chat", key="finalizar-btn"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.session_state.bienvenida_enviada = False
        st.rerun()
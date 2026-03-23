import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

# --- 1. CONFIGURACIÓN Y ESTILOS (Inyectados directamente) ---
st.set_page_config(page_title="CoreDesk Support", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    /* Limpieza de iconos naranja basura */
    [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u, span[data-testid="stWidgetLabel"] { 
        display: none !important; 
    }
    /* Tarjeta de Usuario */
    .user-card-pro {
        background: white; border-radius: 10px; padding: 15px;
        border-left: 6px solid #0E3255; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-top: 10px; margin-bottom: 20px;
    }
    /* Estilo del botón de entrada */
    .stButton>button {
        background-color: #0E3255 !important; color: white !important;
        border-radius: 8px; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP IA (Lógica del primer código) ---
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

try: logo_img = Image.open("logo.png")
except: logo_img = None

# --- 3. NAVEGACIÓN ---

# Caso A: Registro
if st.session_state.user_data is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, use_container_width=True)
        st.markdown("<h1 style='text-align:center; color:#0E3255;'>CoreDesk</h1>", unsafe_allow_html=True)
        with st.form("login"):
            n = st.text_input("Nombre:")
            e = st.text_input("Empresa:")
            if st.form_submit_button("INICIAR SOPORTE"):
                if n and e:
                    st.session_state.user_data = {"nombre": n, "empresa": e, "inicio": time.time()}
                    st.rerun()

# Caso B: Chat (Usando la lógica que sí respondía)
else:
    # Header con Logo y Contador
    col_logo, col_timer = st.columns([8, 1])
    with col_logo:
        if logo_img: st.image(logo_img, width=120)
    with col_timer:
        t_min = int((time.time() - st.session_state.user_data['inicio']) / 60)
        st.write(f"⏱️ {t_min} min")

    st.markdown(f'<div class="user-card-pro">👤 <b>{st.session_state.user_data["nombre"]}</b> | 🏢 {st.session_state.user_data["empresa"]}</div>', unsafe_allow_html=True)
    st.divider()

    # Mostrar Historial
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="🤖" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    # CAJA DE CHAT (Lógica del primer código, la más estable)
    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    # Prompt amable para novatos
                    ctx = f"Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}. Explica de forma sencilla (ej: 'Abre la carpeta naranja'). Pregunta al final si funcionó."
                    
                    # Generación de contenido directa
                    response = model.generate_content(f"{ctx}\n\nPregunta: {prompt}")
                    respuesta = response.text
                    
                    st.markdown(respuesta)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta})
                except Exception as e:
                    st.error(f"Error: {e}")
        st.rerun()

    # Botón lateral para salir (Más estable que el flotante HTML)
    if st.sidebar.button("Finalizar Ticket"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.rerun()
import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3em;
        background-color: #0E3255; color: white; font-weight: bold;
    }
    [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u, span[data-testid="stWidgetLabel"] { 
        display: none !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DE IA (DETECTOR AUTOMÁTICO) ---
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

# --- 3. GESTIÓN DE SESIÓN ---
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None
# NUEVO: Candado de bienvenida
if "bienvenida_enviada" not in st.session_state: st.session_state.bienvenida_enviada = False

try: logo_img = Image.open("logo.png")
except: logo_img = None

# --- 4. INTERFAZ ---

if st.session_state.user_data is None:
    if logo_img: st.image(logo_img, width=200)
    st.markdown("<h1 style='color:#0E3255; text-align:center;'>🛡️ CoreDesk System</h1>", unsafe_allow_html=True)
    with st.form("registro"):
        n = st.text_input("Nombre Completo:")
        e = st.text_input("Empresa:")
        if st.form_submit_button("INGRESAR AL SISTEMA"):
            if n and e:
                st.session_state.user_data = {"nombre": n, "empresa": e}
                st.rerun()
else:
    st.markdown(f"<h2 style='color:#0E3255;'>Soporte: {st.session_state.user_data['empresa']}</h2>", unsafe_allow_html=True)
    st.caption(f"Atendiendo a: **{st.session_state.user_data['nombre']}**")

    # --- LÓGICA DE BIENVENIDA AUTOMÁTICA ---
    if not st.session_state.bienvenida_enviada:
        saludo = f"¡Hola **{st.session_state.user_data['nombre']}**! 👋 Bienvenido al soporte técnico de **CoreDesk**.\n\nEstoy listo para ayudarte con cualquier inconveniente en **{st.session_state.user_data['empresa']}**. ¿Qué problema técnico presentas hoy?"
        st.session_state.messages.append({"role": "assistant", "content": saludo})
        st.session_state.bienvenida_enviada = True

    # Mostrar Historial
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="🤖" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    ctx = f"""
                    Actúa como experto de CoreDesk. Ayudas a {st.session_state.user_data['nombre']} de {st.session_state.user_data['empresa']}.
                    Responde de forma amable y paso a paso para novatos.
                    Incluye siempre:
                    CATEGORÍA: [Hardware/Software/Redes]
                    PRIORIDAD: [Baja/Media/Alta/Crítica]
                    """
                    response = st.session_state.model.generate_content(f"{ctx}\n\nProblema: {prompt}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error al procesar: {e}")
        st.rerun()

    if st.sidebar.button("Finalizar Ticket"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.session_state.bienvenida_enviada = False # Reset para el próximo login
        st.rerun()
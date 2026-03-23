import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")

# Logo
try: 
    logo_img = Image.open("logo.png")
except: 
    logo_img = None

# --- 2. INYECCIÓN DE ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* Ocultar elementos nativos de Streamlit */
    div[data-testid="stHeader"], div[data-testid="stSidebarNav"] { display: none; }
    
    /* Colores de Iconos de Chat */
    [data-testid="stChatMessageAssistant"] [data-testid="stChatMessageAvatar"] {
        background-color: #FF8C00 !important;
        color: white !important;
        border-radius: 50%;
    }
    
    .stChatMessage:not([data-testid="stChatMessageAssistant"]) [data-testid="stChatMessageAvatar"] {
        background-color: #0E3255 !important;
        color: white !important;
        border-radius: 50%;
    }

    /* Limpieza visual */
    [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u, span[data-testid="stWidgetLabel"] { 
        display: none !important; 
    }

    /* Estilo de Botón de Ingreso */
    div[data-testid="stForm"] .stButton>button { 
        background-color: #0E3255 !important; color: white !important; 
        border-radius: 8px; height: 3em; width: 100%; font-weight: bold;
    }

    /* ESTILO PARA EL BOTÓN ROJO DE FINALIZAR (Posición fija) */
    div.stButton > button#finalizar-btn {
        position: fixed;
        bottom: 30px;
        left: 30px;
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 50px;
        width: 150px;
        height: 45px;
        z-index: 1000;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
        font-weight: bold;
    }
    div.stButton > button#finalizar-btn:hover {
        background-color: #E04141 !important;
        transform: scale(1.05);
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
    # --- PANTALLA DE REGISTRO ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_img: st.image(logo_img, width=150)
        st.markdown("<h1 style='color:#0E3255; text-align:center; font-weight:800;'>CoreDesk</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6c757d; margin-bottom: 20px;'>Intelligent IT Management System</p>", unsafe_allow_html=True)
        
        with st.form("registro"):
            n = st.text_input("Nombre Completo:")
            e = st.text_input("Empresa o Departamento:")
            if st.form_submit_button("INGRESAR AL SISTEMA"):
                if n and e:
                    # Guardamos el tiempo de inicio aquí
                    st.session_state.user_data = {"nombre": n, "empresa": e, "inicio": time.time()}
                    st.rerun()
                else:
                    st.error("Por favor rellena ambos campos.")

else:
    # --- PANTALLA DE CHAT ACTIVA ---
    
    # 1. Header Fijo con Logo
    st.markdown('<div style="position: fixed; top: 0; left: 0; width: 100%; height: 70px; background-color: white; z-index: 999; display: flex; align-items: center; padding: 0 5%; border-bottom: 1px solid #EEE;">', unsafe_allow_html=True)
    if logo_img:
        st.image(logo_img, width=100)
    
    # FIX: Usar .get() para evitar el KeyError
    inicio_ticket = st.session_state.user_data.get('inicio', time.time())
    t_min = int((time.time() - inicio_ticket) / 60)
    
    st.markdown(f'<div style="margin-left: auto; color: #6c757d; font-weight: bold;">⏱️ {t_min} min activo</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="margin-top: 90px;"></div>', unsafe_allow_html=True)

    # Tarjeta Usuario
    st.markdown(f"""
        <div style="background:white; padding:15px; border-radius:10px; border-left:5px solid #0E3255; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
            👤 <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Lógica de Bienvenida
    if not st.session_state.bienvenida_enviada:
        saludo = f"¡Hola **{st.session_state.user_data['nombre']}**! 👋 Bienvenido al soporte técnico de **CoreDesk**.\n\n¿Qué problema técnico presentas hoy?"
        st.session_state.messages.append({"role": "assistant", "content": saludo})
        st.session_state.bienvenida_enviada = True

    # Historial de Chat
    for m in st.session_state.messages:
        av = "🤖" if m["role"] == "assistant" else "👤"
        with st.chat_message(m["role"], avatar=av):
            st.markdown(m["content"])

    # Caja de entrada
    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    ctx = f"Actúa como experto de CoreDesk. Ayudas a {st.session_state.user_data['nombre']}. Explica paso a paso para novatos. CATEGORÍA y PRIORIDAD al inicio."
                    response = st.session_state.model.generate_content(f"{ctx}\n\nProblema: {prompt}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error al procesar: {e}")
        st.rerun()

    # --- 2. BOTÓN ROJO DE FINALIZAR CHAT (Nativo con estilo fijo) ---
    if st.button("Finalizar Chat", key="finalizar-btn"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.session_state.bienvenida_enviada = False
        st.rerun()
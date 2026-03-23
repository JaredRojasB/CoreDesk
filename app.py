import streamlit as st
import google.generativeai as genai
import os, time
from PIL import Image

# --- 1. CONFIGURACIÓN DE PÁGINA ---
# Usamos layout="wide" para tener más espacio para el header y el chat.
st.set_page_config(page_title="CoreDesk Support", page_icon="🛡️", layout="wide")

# Logo (Lo cargamos al principio para usarlo en el Header y Registro)
try: 
    logo_img = Image.open("logo.png")
except: 
    logo_img = None

# --- 2. INYECCIÓN DE ESTILOS CSS (Todo dentro de este archivo) ---
st.markdown("""
    <style>
    /* Fondo Blanco Puro */
    .stApp { background-color: #FFFFFF; }
    
    /* Ocultar elementos nativos molestos de Streamlit (Barra superior y menús) */
    div[data-testid="stHeader"], div[data-testid="stSidebarNav"] { display: none; }
    
    /* --- ESTILOS DE CHAT (COLORES DE ICONOS) --- */
    /* Icono del Bot (Robot🤖) -> Color NARANJA CoreDesk */
    [data-testid="stChatMessageAssistant"] [data-testid="stChatMessageAvatar"] {
        background-color: #FF8C00 !important; /* Naranja fuerte */
        color: white !important;
        border-radius: 50%;
    }
    
    /* Icono del Usuario (Persona👤) -> Color AZUL CoreDesk */
    .stChatMessage:not([data-testid="stChatMessageAssistant"]) [data-testid="stChatMessageAvatar"] {
        background-color: #0E3255 !important; /* Azul Marino CoreDesk */
        color: white !important;
        border-radius: 50%;
    }

    /* Ocultar cuadros naranjas basura de error visual */
    [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u, span[data-testid="stWidgetLabel"] { 
        display: none !important; 
    }

    /* --- ESTILOS DE REGISTRO Y BOTONES --- */
    .core-title-auth { 
        color: #0E3255; font-size: 40px; font-weight: 800; 
        text-align: center; margin-bottom: 10px; 
    }
    
    /* Botón de Ingreso (Azul) */
    div[data-testid="stForm"] .stButton>button { 
        background-color: #0E3255 !important; color: white !important; 
        border-radius: 8px; height: 3em; width: 100%; font-weight: bold;
    }

    /* --- ESTILOS DEL BOTÓN ROJO DE FINALIZAR (Flotante) --- */
    #btn-finalizar-rojo {
        position: fixed;
        bottom: 30px;
        left: 30px;
        background-color: #FF4B4B; /* Rojo intenso de advertencia */
        color: white !important;
        padding: 12px 24px;
        border-radius: 50px;
        font-weight: bold;
        text-decoration: none;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
        transition: 0.3s ease;
        border: none;
        cursor: pointer;
    }
    #btn-finalizar-rojo:hover {
        background-color: #E04141; /* Rojo más oscuro al pasar el mouse */
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE IA (TU LÓGICA FUNCIONAL INTACTA) ---
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
        # 1. Logo estándar en el registro
        if logo_img: st.image(logo_img, width=150) # Tamaño estándar
        st.markdown("<h1 class='core-title-auth'>CoreDesk</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6c757d; margin-bottom: 20px;'>Intelligent IT Management System</p>", unsafe_allow_html=True)
        
        with st.form("registro"):
            n = st.text_input("Nombre Completo:")
            e = st.text_input("Empresa o Departamento:")
            if st.form_submit_button("INGRESAR AL SISTEMA"):
                if n and e:
                    st.session_state.user_data = {"nombre": n, "empresa": e, "inicio": time.time()}
                    st.rerun()
                else:
                    st.error("Por favor rellena ambos campos.")

else:
    # --- PANTALLA DE CHAT ACTIVA ---
    
    # 1. HEADER FIJO CON LOGO (Superior Izquierda)
    st.markdown('<div class="header-fixed" style="position: fixed; top: 0; left: 0; width: 100%; height: 70px; background-color: white; z-index: 999; display: flex; align-items: center; padding: 0 5%; border-bottom: 1px solid #EEE;">', unsafe_allow_html=True)
    
    # Columna para el logo (Tamaño estándar)
    if logo_img:
        st.image(logo_img, width=100) # Logo legible pero no invasivo
    
    # Columna para el contador de tiempo (Derecha)
    t_min = int((time.time() - st.session_state.user_data['inicio']) / 60)
    st.markdown(f'<div style="margin-left: auto; color: #6c757d; font-weight: bold;">⏱️ {t_min} min activo</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Espaciado para que el chat no se pegue al header fijo
    st.markdown('<div style="margin-top: 90px;"></div>', unsafe_allow_html=True)

    # Tarjeta Usuario Formal
    st.markdown(f"""
        <div style="background:white; padding:15px; border-radius:10px; border-left:5px solid #0E3255; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
            👤 <b>{st.session_state.user_data['nombre']}</b> | 🏢 {st.session_state.user_data['empresa']}
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --- LÓGICA DE BIENVENIDA AUTOMÁTICA ---
    if not st.session_state.bienvenida_enviada:
        saludo = f"¡Hola **{st.session_state.user_data['nombre']}**! 👋 Bienvenido al soporte técnico de **CoreDesk**.\n\nEstoy listo para ayudarte con cualquier inconveniente en **{st.session_state.user_data['empresa']}**. ¿Qué problema técnico presentas hoy?"
        st.session_state.messages.append({"role": "assistant", "content": saludo})
        st.session_state.bienvenida_enviada = True

    # 3. MOSTRAR HISTORIAL CON ICONOS DE COLORES (Azul y Naranja)
    for m in st.session_state.messages:
        # Forzamos avatar de emoji para que el CSS lo pinte del color correcto
        avatar_type = "🤖" if m["role"] == "assistant" else "👤"
        with st.chat_message(m["role"], avatar=avatar_type):
            st.markdown(m["content"])

    # CAJA DE ENTRADA
    if prompt := st.chat_input("Escribe tu duda técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Avatar Usuario (Persona👤)
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Avatar Bot (Robot🤖)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
                try:
                    ctx = f"""
                    Actúa como experto de CoreDesk. Ayudas a {st.session_state.user_data['nombre']} de {st.session_state.user_data['empresa']}.
                    Responde de forma amable y paso a paso para novatos.
                    Incluye siempre al inicio:
                    CATEGORÍA: [Hardware/Software/Redes]
                    PRIORIDAD: [Baja/Media/Alta/Crítica]
                    """
                    response = st.session_state.model.generate_content(f"{ctx}\n\nProblema: {prompt}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error al procesar: {e}")
        st.rerun()

    # --- 2. BOTÓN ROJO DE FINALIZAR CHAT (Inferior Izquierda - Flotante) ---
    # Usamos un botón de Streamlit pero inyectado con HTML para controlarlo con CSS
    if st.markdown('<button id="btn-finalizar-rojo">⚠️ Finalizar Chat</button>', unsafe_allow_html=True):
        # Lógica de cierre (Streamlit detecta si el 'button' de HTML fue clickeado)
        st.session_state.user_data = None
        st.session_state.messages = []
        st.session_state.bienvenida_enviada = False # Reset para el próximo login
        st.rerun()
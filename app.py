import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import auth_styles
import chat_styles

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CoreDesk Support", layout="wide")

# IA Setup
api_key = st.secrets.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None
if "bienvenida_enviada" not in st.session_state: st.session_state.bienvenida_enviada = False

try: logo_img = Image.open("logo.png")
except: logo_img = None

if st.session_state.user_data is None:
    auth_styles.aplicar_auth()
    # ... (Tu código de login igual que antes)
else:
    chat_styles.aplicar_chat()
    
    # 1. Header (Logo Izquierda)
# --- Calcular tiempo ---
t_min = int((time.time() - st.session_state.user_data['inicio']) / 60)

# --- Tarjeta Formal ---
st.markdown(f"""
    <div class="user-card-formal">
        <div>
            <div style="color: #6c757d; font-size: 12px;">SOPORTE ACTIVO</div>
            <div style="color: #0E3255; font-size: 18px; font-weight: bold;">👤 {st.session_state.user_data['nombre']}</div>
            <div style="color: #495057;">🏢 {st.session_state.user_data['empresa']}</div>
        </div>
        <div style="text-align: right;">
            <div style="color: #6c757d; font-size: 12px;">TIEMPO TRANSCURRIDO</div>
            <div style="color: #0E3255; font-size: 20px; font-weight: bold;">⏱️ {t_min} min</div>
        </div>
    </div>
""", unsafe_allow_html=True)

if "bienvenida_enviada" not in st.session_state:
    with st.chat_message("assistant", avatar="🤖"):
        msg = f"¡Hola **{st.session_state.user_data['nombre']}**! Soy tu Asistente de CoreDesk. ¿En qué puedo ayudarte hoy?"
        st.markdown(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})
    st.session_state.bienvenida_enviada = True # Candado para que no se repita

    # 3. BIENVENIDA ÚNICA (Corregida)
    if not st.session_state.bienvenida_enviada:
        saludo = f"¡Hola **{st.session_state.user_data['nombre']}**! Soy tu Asistente de CoreDesk. ¿En qué puedo ayudarte hoy?"
        st.session_state.messages.append({"role": "assistant", "content": saludo})
        st.session_state.bienvenida_enviada = True

    # 4. Historial (Avatar Robot Azul y Usuario)
for m in st.session_state.messages:
    # Asignamos icono según el rol: Robot para bot, Persona para Jared
    avatar_icon = "🤖" if m["role"] == "assistant" else "👤"
    with st.chat_message(m["role"], avatar=avatar_icon):
        st.markdown(m["content"])

    # 5. Entrada de Chat con Popover (Clip azul a la izquierda)
    c_clip, c_txt = st.columns([1, 15])
    with c_clip:
        with st.popover("📎"):
            st.button("📷 Subir Imagen", disabled=True)

    if prompt := st.chat_input("Describe tu problema técnico aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("CoreDesk AI analizando..."):
                # PROMPT PROCEDIMENTAL ESPECÍFICO
                ctx = f"""Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}. 
                Sé extremadamente específico: No digas 'borra archivos', di 'Presiona Win + R, escribe temp, selecciona todo y presiona Shift + Del'."""
                res = model.start_chat(history=[]).send_message(f"{ctx}\n{prompt}").text
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
        st.rerun()

   # Botón X Roja Flotante (Enlace que reinicia la app)
st.markdown('<a href="/" target="_self" id="finalizar-btn-flotante" title="Finalizar Chat"></a>', unsafe_allow_html=True)
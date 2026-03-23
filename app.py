import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from datetime import datetime
from PIL import Image

# IMPORTAMOS TUS MÓDULOS DE ESTILO Y AUTH
import styles
import auth

# --- CONFIGURACIÓN ---
# Usamos layout="wide" para un mejor diseño responsivo del chat
st.set_page_config(page_title="CoreDesk Support AI", page_icon="🛡️", layout="wide")
styles.aplicar_estilos() # Aplicamos la pintura GLOBAL organizada por secciones

# --- IA SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Gestión de Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "user_data" not in st.session_state: st.session_state.user_data = None

# --- CARGA DE LOGO (Referencia a 'logo.png') ---
# Asegúrate de que el archivo se llame exactamente 'logo.png' en tu Codespace
logo_path = "logo.png"
logo_available = False
try:
    logo_img = Image.open(logo_path)
    logo_available = True
except:
    # Si no la encuentra, logo_available se mantiene False y usaremos el emoji
    pass

# --- LÓGICA DE NAVEGACIÓN ---

# Caso A: Pantalla de Registro (Logo GRANDE y CENTRADO como Banner)
if st.session_state.user_data is None:
    # Banner Principal (Solo visible en registro)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        if logo_available:
            # Mostramos el logo grande aquí, como banner
            st.image(logo_img, use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center;'>🛡️</h1>", unsafe_allow_html=True)
    st.markdown("<p class='core-title' style='text-align: center;'>CoreDesk</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6c757d;'>Sistema de Soporte Técnico Inteligente</p>", unsafe_allow_html=True)
    
    # Mostramos el formulario de auth (este ya está limpio en su propio archivo)
    auth.mostrar_registro()

# Caso B: Pantalla de Chat Activo (Logo PEQUEÑO en IZQUIERDA)
else:
    # BARRA SUPERIOR DEL CHAT
    # Separamos en 3 columnas: Logo (Pequño y a la izq), Usuario, Botón Finalizar (Rojo y a la der)
    # columns([1, 12, 1]) da un ancho sutil al logo, balanceando la interfaz
    c_logo, c_user, c_fin = st.columns([1, 12, 1]) 
    
    with c_logo:
        # AQUÍ PONEMOS EL LOGO PEQUEÑO Y RESPONSIVO (A LA IZQUIERDA)
        if logo_available:
            # Creamos un contenedor HTML para el CSS responsivo (.chat-logo-container)
            st.markdown('<div class="chat-logo-container">', unsafe_allow_html=True)
            st.image(logo_img, use_container_width=True) # El CSS controlará el max-width (80px)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with c_user:
        # Información del usuario centrada sutilmente
        st.write(f"Soporte Activo: **{st.session_state.user_data['nombre']}** | {st.session_state.user_data['empresa']}")
    
    with c_fin:
        # AQUÍ ESTÁ EL BOTÓN FINALIZAR (ROJO)
        # Envolvemos en el div para aplicar el CSS (.btn-finalizar)
        st.markdown('<div class="btn-finalizar">', unsafe_allow_html=True)
        if st.button("FINALIZAR", key="finalizar_chat_btn"):
            with st.spinner("Cerrando ticket de forma segura..."):
                time.sleep(0.5)
                st.session_state.user_data = None
                st.session_state.messages = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---") # Línea divisoria

    # HISTORIAL DE MENSAJES (Ahora con padding para el input fijo)
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): 
            st.markdown(m["content"])

    # ENTRADA DE CHAT CON CLIP Y BARRA FIJA (Controlado por CSS)
    col_clip, col_txt = st.columns([1, 15])
    with col_clip:
        # Usamos popover para el menú desplegable del clip
        menu_archivos = st.popover("📎", help="Adjuntar archivos")
        with menu_archivos:
            st.write("Selecciona archivo:")
            # Botón inactivo por ahora
            st.button("📷 Imagen del problema (Hardware)", disabled=True)

    with col_txt:
        if prompt := st.chat_input("Escribe tu duda técnica aquí...", key="chat_input_val"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): 
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("CoreDesk AI analizando..."):
                    try:
                        system_prompt = f"""
                        Eres Soporte CoreDesk. Guía paso a paso a {st.session_state.user_data['nombre']}.
                        1. Identifícate como 'Asistente IA de CoreDesk'.
                        2. Responde con un formato de 'GUÍA PASO A PASO'.
                        3. Usa negritas para componentes de hardware y comandos.
                        4. Al final pregunta EXACTAMENTE: '¿Te funcionó la información que te di?'
                        """
                        chat = model.start_chat(history=[])
                        full_prompt = f"{system_prompt}\nProblema: {prompt}"
                        response = chat.send_message(full_prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Error de red: {e}")
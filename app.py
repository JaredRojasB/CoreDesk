import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Configuración de página
st.set_page_config(page_title="CoreDesk AI Chat", page_icon="💬")

# 1. CARGAR CONFIGURACIÓN (Nube o Local)
load_dotenv()
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ Configuración faltante: Agrega GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=api_key)

# 2. INICIALIZAR EL MODELO (Aseguramos que 'model' exista siempre)
if "model_name" not in st.session_state:
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.session_state.model_name = next((m for m in modelos if "flash" in m), modelos[0])
    except Exception as e:
        st.error(f"Error al conectar con Google: {e}")
        st.stop()

# Creamos el objeto del modelo fuera de cualquier condición
model = genai.GenerativeModel(st.session_state.model_name)

# 3. HISTORIAL Y DATOS DEL USUARIO
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# --- PANTALLA DE REGISTRO ---
if st.session_state.user_data is None:
    st.title("🛡️ Registro de Incidencia - CoreDesk")
    with st.form("registro"):
        nombre = st.text_input("Nombre Completo:")
        empresa = st.text_input("Empresa:")
        submit = st.form_submit_button("Entrar al Soporte")
        
        if submit:
            if nombre and empresa:
                st.session_state.user_data = {"nombre": nombre, "empresa": empresa}
                st.rerun()
            else:
                st.error("Por favor llena todos los campos.")
else:
    # --- INTERFAZ DE CHAT ---
    st.title(f"🖥️ CoreDesk Support")
    st.caption(f"Usuario: {st.session_state.user_data['nombre']} | Empresa: {st.session_state.user_data['empresa']}")

    # Mostrar mensajes previos
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del chat
    if prompt := st.chat_input("¿En qué puedo ayudarte?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("CoreDesk analizando..."):
                try:
                    contexto = f"Eres el asistente de soporte de CoreDesk. Atiendes a {st.session_state.user_data['nombre']} de la empresa {st.session_state.user_data['empresa']}."
                    # Usamos el objeto 'model' que ya definimos arriba
                    chat = model.start_chat(history=[])
                    response = chat.send_message(f"{contexto}\nProblema: {prompt}")
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error al generar respuesta: {e}")

    # Botón lateral
    if st.sidebar.button("Cerrar Ticket"):
        st.session_state.user_data = None
        st.session_state.messages = []
        st.rerun()
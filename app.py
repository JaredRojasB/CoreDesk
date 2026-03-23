import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO ---
st.set_page_config(
    page_title="CoreDesk Support AI", 
    page_icon="🛡️", 
    layout="centered"
)

# Inyección de CSS para personalizar la interfaz
st.markdown("""
    <style>
    /* Color de fondo principal */
    .stApp {
        background-color: #f8f9fa;
    }
    /* Estilo de los botones */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #0E3255;
        color: white;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1a4a7a;
        color: white;
    }
    /* Títulos personalizados */
    .main-title {
        color: #0E3255;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Estilo de los inputs */
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DE IA (Nube o Local) ---
load_dotenv()
# Buscamos la llave en los Secrets de Streamlit (Prioridad) o en el .env
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ Configuración faltante: Agrega GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=api_key)

# Inicialización segura del modelo
if "model_name" not in st.session_state:
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.session_state.model_name = next((m for m in modelos if "flash" in m), modelos[0])
    except:
        st.session_state.model_name = "gemini-1.5-flash"

model = genai.GenerativeModel(st.session_state.model_name)

# --- 3. FUNCIONES DE GUARDADO (Bitácora) ---
def guardar_en_bitacora(nombre, empresa, problema, respuesta):
    archivo_bitacora = "bitacora_coredesk.csv"
    nueva_entrada = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuario": nombre,
        "Empresa": empresa,
        "Problema": problema,
        "Solucion_IA": respuesta.replace('\n', ' ') # Limpiamos saltos de línea para el CSV
    }
    
    df_nueva = pd.DataFrame([nueva_entrada])
    
    # Si el archivo no existe, lo creamos con cabeceras. Si existe, añadimos sin cabecera.
    if not os.path.isfile(archivo_bitacora):
        df_nueva.to_csv(archivo_bitacora, index=False, encoding='utf-8')
    else:
        df_nueva.to_csv(archivo_bitacora, mode='a', header=False, index=False, encoding='utf-8')

# --- 4. GESTIÓN DE ESTADO DE SESIÓN ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# --- INTERFAZ DE USUARIO ---

# Caso A: El usuario no se ha registrado
if st.session_state.user_data is None:
    st.markdown("<h1 class='main-title'>🛡️ CoreDesk System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Plataforma Inteligente de Gestión de Incidencias IT</p>", unsafe_allow_html=True)
    
    with st.container():
        st.info("Por favor, identifícate para comenzar el soporte técnico.")
        with st.form("registro_form"):
            nombre = st.text_input("Nombre Completo:")
            empresa = st.text_input("Empresa o Departamento:")
            btn_entrar = st.form_submit_button("INGRESAR AL SISTEMA")
            
            if btn_entrar:
                if nombre and empresa:
                    st.session_state.user_data = {"nombre": nombre, "empresa": empresa}
                    st.rerun()
                else:
                    st.warning("Debes completar ambos campos para continuar.")

# Caso B: El usuario ya está registrado (Chat activo)
else:
    st.markdown(f"<h2 class='main-title'>Soporte Activo: {st.session_state.user_data['empresa']}</h2>", unsafe_allow_html=True)
    st.caption(f"Atendiendo a: **{st.session_state.user_data['nombre']}**")

    # Mostrar el historial de chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Caja de entrada de chat
    if prompt := st.chat_input("¿Cuál es el problema técnico hoy?"):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Respuesta de la IA con el System Prompt refinado
        with st.chat_message("assistant"):
            with st.spinner("CoreDesk AI está analizando la solución..."):
                try:
                    system_prompt = f"""
                    Eres el experto de Soporte Técnico de la plataforma CoreDesk. 
                    Estás ayudando a {st.session_state.user_data['nombre']} de la empresa {st.session_state.user_data['empresa']}.
                    
                    INSTRUCCIONES DE FORMATO:
                    1. Identifícate como 'Asistente IA de CoreDesk'. No uses otros nombres.
                    2. Organiza la solución en pasos numerados o puntos (bullet points).
                    3. Usa negritas para resaltar términos técnicos importantes.
                    4. Mantén un tono profesional pero amable.
                    5. Al final de tu respuesta, pregunta EXACTAMENTE: "¿Te funcionó la información que te di?"
                    """
                    
                    chat = model.start_chat(history=[])
                    full_query = f"{system_prompt}\n\nProblema del usuario: {prompt}"
                    response = chat.send_message(full_query)
                    
                    respuesta_final = response.text
                    
                    # Mostrar y guardar respuesta
                    st.markdown(respuesta_final)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta_final})
                    
                    # Guardar automáticamente en la bitácora
                    guardar_en_bitacora(
                        st.session_state.user_data['nombre'],
                        st.session_state.user_data['empresa'],
                        prompt,
                        respuesta_final
                    )
                except Exception as e:
                    st.error(f"Hubo un error al procesar tu solicitud: {e}")

    # --- BARRA LATERAL (ADMIN) ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2906/2906274.png", width=100)
        st.title("Panel de Control")
        
        if st.button("Finalizar Ticket / Salir"):
            st.session_state.user_data = None
            st.session_state.messages = []
            st.rerun()
            
        st.markdown("---")
        st.subheader("📊 Administración")
        
        # Botón para descargar la bitácora si existe
        if os.path.exists("bitacora_coredesk.csv"):
            df_log = pd.read_csv("bitacora_coredesk.csv")
            st.download_button(
                label="📥 Descargar Bitácora (CSV)",
                data=df_log.to_csv(index=False).encode('utf-8'),
                file_name=f"bitacora_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.write("Aún no hay registros en la bitácora.")
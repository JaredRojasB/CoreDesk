import streamlit as st

def aplicar_estilos():
    st.markdown("""
        <style>
        /* ==========================================
           1. DISEÑO GLOBAL (General)
           ========================================== */
        .stApp { 
            background-color: #f4f7f9; 
        }
        
        .core-title { 
            color: #0E3255; 
            font-size: 55px; 
            font-weight: 800; 
            text-align: center; 
            margin-bottom: 0px; 
        }

        .stSpinner > div { 
            border-top-color: #0E3255 !important; 
        }

        /* ==========================================
           2. INICIO (Login / Registro) - Logo GRANDE
           ========================================== */
        /* Estilo del botón "Iniciar Soporte" dentro del formulario */
        div[data-testid="stForm"] .stButton>button { 
            background-color: #0E3255 !important; 
            color: white !important; 
            height: 3.5em; 
            width: 100%; 
            border-radius: 10px;
            font-weight: bold;
            border: 2px solid #0E3255;
        }
        
        div[data-testid="stForm"] .stButton>button:hover {
            background-color: #ffffff !important;
            color: #0E3255 !important;
        }

        /* ==========================================
           3. CHAT (Interfaz de Usuario Activa)
           ========================================== */
        /* 3a. Estilo del Logo PEQUEÑO y Responsivo (Izquierda) */
        .chat-logo-container img {
            max-width: 80px; /* Tamaño máximo sutil */
            height: auto;
            border-radius: 5px;
        }

        /* 3b. Botón de "Finalizar" Rojo (Esquina Superior Derecha) */
        .btn-finalizar > button {
            background-color: #d9534f !important;
            color: white !important;
            border: 2px solid #d9534f !important;
            border-radius: 10px;
            font-weight: bold;
            transition: 0.3s;
        }

        .btn-finalizar > button:hover {
            background-color: #c9302c !important;
            border-color: #c9302c !important;
            color: white !important;
        }

        /* 3c. Burbujas de Chat Mejoradas */
        .stChatMessage { 
            border-radius: 20px; 
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 10px;
        }

        /* 3d. Estilo del Popover (Clip 📎) */
        /* Aseguramos que el botón del clip no sea blanco */
        button[data-testid="stBaseButton-headerNoPadding"] {
            border-radius: 50%;
            background-color: #e9ecef !important;
            color: #495057 !important;
        }

        /* 3e. BARRA DE CHAT FIJA ABAJO (The Magic Part) */
        /* Pegamos el contenedor de entrada al fondo */
        div[data-testid="stChatInput"] {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 80%; /* Ancho responsivo del input */
            z-index: 999; /* Asegura que esté por encima de los mensajes */
            background-color: white;
            border-radius: 15px;
            padding: 10px;
            box-shadow: 0px -5px 15px rgba(0,0,0,0.1);
        }

        /* Agregamos padding al fondo de la app para que el último mensaje no se tape */
        .stApp {
            padding-bottom: 150px; /* Espacio para el input fijo */
        }
        </style>
    """, unsafe_allow_html=True)
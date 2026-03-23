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
           2. INICIO (Login / Registro)
           ========================================== */
        /* Estilo del botón "Iniciar Soporte" dentro del formulario */
        div[data-testid="stForm"] .stButton>button { 
            background-color: #0E3255; 
            color: white; 
            height: 3.5em; 
            width: 100%; 
            border-radius: 10px;
            font-weight: bold;
        }
        
        div[data-testid="stForm"] .stButton>button:hover {
            background-color: #1a4a7a;
            border-color: #1a4a7a;
        }

        /* ==========================================
           3. CHAT (Interfaz de Usuario)
           ========================================== */
        /* Burbujas de Chat */
        .stChatMessage { 
            border-radius: 20px; 
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        }

        /* Contenedor del Logo PEQUEÑO y RESPONSIVO en el Chat */
        .chat-logo-container {
            display: flex;
            justify-content: flex-end; /* Alinea a la derecha */
            align-items: center;
            padding: 10px;
            width: 100%;
        }

        /* Estilo de la imagen del logo dentro del chat (pequeña) */
        .chat-logo-container img {
            max-width: 80px; /* Tamaño máximo responsivo */
            height: auto;
            border-radius: 5px;
        }

        /* Botón de "Finalizar" Rojo (Esquina Superior) */
        .btn-finalizar > button {
            background-color: #d9534f !important;
            color: white !important;
            border: none !important;
            border-radius: 10px;
            font-weight: bold;
        }

        .btn-finalizar > button:hover {
            background-color: #c9302c !important;
        }

        /* Estilo del Popover (Clip 📎) */
        button[data-testid="stBaseButton-headerNoPadding"] {
            border-radius: 50%;
            background-color: #e9ecef;
        }

        </style>
    """, unsafe_allow_html=True)
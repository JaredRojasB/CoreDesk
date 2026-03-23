import streamlit as st

def aplicar_estilos():
    st.markdown("""
        <style>
        /* --- 1. DISEÑO GLOBAL --- */
        .stApp { background-color: #f4f7f9; }
        .core-title { color: #0E3255; font-size: 55px; font-weight: 800; text-align: center; }
        .stSpinner > div { border-top-color: #0E3255 !important; }

        /* --- 2. INICIO --- */
        div[data-testid="stForm"] .stButton>button { 
            background-color: #0E3255 !important; color: white !important; 
            border-radius: 10px; font-weight: bold;
        }

        /* --- 3. CHAT (CAMBIOS SOLICITADOS) --- */
        
        /* Logo pequeño arriba a la izquierda */
        .chat-logo-container img {
            max-width: 100px;
            height: auto;
            margin-bottom: 10px;
        }

        /* INFO USUARIO (Apartado separado) */
        .user-info-box {
            background-color: #e9ecef;
            padding: 10px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: #0E3255;
            font-weight: 600;
        }

        /* BOTÓN FINALIZAR (FORZADO A ROJO) */
        /* Usamos selectores de atributo para asegurar el color */
        button[kind="secondary"] {
            background-color: #d9534f !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
        }
        button[kind="secondary"]:hover {
            background-color: #c9302c !important;
        }

        /* BARRA DE CHAT FIJA CON BOTÓN '+' */
        div[data-testid="stChatInput"] {
            position: fixed;
            bottom: 30px;
            z-index: 1000;
            padding-left: 60px; /* Espacio para el botón + */
        }

        /* Botón '+' integrado */
        .plus-button-container {
            position: fixed;
            bottom: 42px;
            left: calc(50% - 345px); /* Ajuste según el ancho del chat */
            z-index: 1001;
        }
        
        /* Responsive para el plus button */
        @media (max-width: 1200px) {
            .plus-button-container { left: 5%; }
        }
        </style>
    """, unsafe_allow_html=True)
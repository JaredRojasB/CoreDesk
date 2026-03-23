import streamlit as st

def aplicar_estilos():
    st.markdown("""
        <style>
        /* --- DISEÑO GLOBAL --- */
        .stApp { background-color: #FFFFFF; }
        
        /* --- HEADER PERSONALIZADO --- */
        .custom-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            background-color: white;
            border-bottom: 1px solid #eee;
            margin-bottom: 20px;
        }

        /* Logo pequeño (Izq) */
        .logo-chat {
            max-width: 80px;
            height: auto;
        }

        /* BOTÓN FINALIZAR (Rojo Forzado) */
        /* Usamos el ID de Streamlit para asegurar el color */
        button[kind="secondary"] {
            background-color: #FF4B4B !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
        }

        /* --- BARRA DE CHAT FIJA ABAJO --- */
        /* Streamlit ya fija el chat_input abajo por defecto, 
           solo vamos a darle espacio para que no se encime */
        .stChatMessage { margin-bottom: 20px; border-radius: 15px; }
        
        /* Estilo para el '+' dentro de la barra */
        .plus-inline {
            display: inline-flex;
            align-items: center;
            margin-right: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        /* Fondo Blanco Puro */
        .stApp { background-color: #FFFFFF; }
        
        /* Ocultar elementos nativos de Streamlit */
        div[data-testid="stHeader"], div[data-testid="stSidebarNav"] { display: none; }
        
        /* MATAR DEFINITIVAMENTE ICONOS NARANJAS (smart_toy / expand_more) */
        [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u, span[data-testid="stWidgetLabel"] { 
            display: none !important; 
        }

        /* 🛡️ FIX DEFINITIVO DE CAPA GRIS Y CARGA 🛡️ */
        /* Ocultar el icono cargando (el mono/bicicleta) */
        [data-testid="stStatusWidget"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Ocultar TODAS las capas grises de carga, forzando transparencia total */
        div[data-testid="stStatusWidgetOverlay"], 
        .st-emotion-cache-p5m09v, 
        .st-emotion-cache-1ae8k9u {
            background-color: rgba(255, 255, 255, 0) !important; /* Transparente puro */
            opacity: 0 !important;
            pointer-events: none !important; /* Permite hacer clic a través de ella */
        }
        
        /* Asegurar que el fondo del chat no cambie */
        [data-testid="stChatMessage"] {
            background-color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)
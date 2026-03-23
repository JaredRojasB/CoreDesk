import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        /* Fondo Blanco Puro */
        .stApp { background-color: #FFFFFF !important; }
        
        /* 🚫 BLOQUEO TOTAL DE CAPA GRIS Y OVERLAYS 🚫 */
        /* Eliminamos cualquier capa que Streamlit ponga encima al cargar */
        div[data-testid="stStatusWidgetOverlay"], 
        .st-emotion-cache-p5m09v, 
        .st-emotion-cache-1ae8k9u,
        div[class*="stStatusWidget"] {
            background-color: transparent !important;
            backdrop-filter: none !important;
            display: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }

        /* Ocultar iconos basura naranja (smart_toy / expand_more) */
        [data-testid="stIconMaterial"], span[data-testid="stWidgetLabel"] { 
            display: none !important; 
        }

        /* Tarjeta de Usuario Profesional */
        .user-card-pro {
            background: white; border-radius: 10px; padding: 15px;
            border-left: 6px solid #0E3255; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-top: 10px; margin-bottom: 20px;
        }

        /* Input de Chat Limpio */
        div[data-testid="stChatInput"] {
            border: 1px solid #e0e0e0 !important;
            border-radius: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)
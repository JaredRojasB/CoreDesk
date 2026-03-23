import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        /* Fondo Blanco */
        .stApp { background-color: #FFFFFF; }
        
        /* Limpieza de iconos naranja */
        [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u, span[data-testid="stWidgetLabel"] { 
            display: none !important; 
        }

        /* Tarjeta de Usuario */
        .user-card-pro {
            background: white; border-radius: 10px; padding: 15px;
            border-left: 6px solid #0E3255; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-top: 10px; margin-bottom: 20px;
        }
        
        /* Suavizar la capa de carga sin romper el bot */
        div[data-testid="stStatusWidgetOverlay"] {
            background-color: rgba(255, 255, 255, 0.5) !important;
            backdrop-filter: blur(2px);
        }
        </style>
    """, unsafe_allow_html=True)
import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; }
        
        /* Limpieza de iconos basura (smart_toy, etc) */
        span[data-testid="stWidgetLabel"], [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u { 
            display: none !important; 
        }

        /* Tarjeta de Usuario */
        .user-card-pro {
            background: white; border-radius: 10px; padding: 15px;
            border-left: 5px solid #0E3255; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-top: 10px; margin-bottom: 20px;
        }

        /* Estilo básico para el chat input para que no se desfase */
        div[data-testid="stChatInput"] {
            border-radius: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)
import streamlit as st

def aplicar_auth():
    st.markdown("""
        <style>
        /* Fondo Blanco Solo Inicio */
        .stApp { background-color: #FFFFFF; }
        
        /* Título Principal */
        .core-title-auth { 
            color: #0E3255; font-size: 55px; font-weight: 800; 
            text-align: center; margin-top: 50px; 
        }
        
        /* Tarjeta del Formulario */
        div[data-testid="stForm"] {
            border: 1px solid #E0E0E0; border-radius: 15px;
            padding: 30px; box-shadow: 0px 5px 20px rgba(0,0,0,0.05);
            background-color: #fcfcfc;
        }

        /* Botón Iniciar Soporte */
        div[data-testid="stForm"] .stButton>button { 
            background-color: #0E3255 !important; color: white !important; 
            border-radius: 8px; height: 3.5em; width: 100%; font-weight: bold;
        }

        /* Matar iconos basura de Streamlit en esta página */
        span[data-testid="stWidgetLabel"], [data-testid="stIconMaterial"], .st-emotion-cache-1ae8k9u { 
            display: none !important; 
        }
        </style>
    """, unsafe_allow_html=True)
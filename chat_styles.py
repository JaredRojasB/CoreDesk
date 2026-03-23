import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        /* --- 1. LIMPIEZA DE ICONOS NARANJAS (smart_toy, etc) --- */
        [data-testid="stIconMaterial"], 
        .st-emotion-cache-1ae8k9u, 
        span[data-testid="stWidgetLabel"] { 
            display: none !important; 
        }

        /* --- 2. CONFIGURACIÓN DE PANTALLA --- */
        .stApp { background-color: #FFFFFF; padding-top: 80px; }
        div[data-testid="stHeader"] { display: none; }

        /* --- 3. CABECERA FIJA --- */
        .header-fixed {
            position: fixed; top: 0; left: 0; width: 100%; height: 70px;
            background: white; z-index: 1000; display: flex;
            align-items: center; padding: 0 5%; border-bottom: 1px solid #EEE;
        }

        /* --- 4. TARJETA DE USUARIO FORMAL --- */
        .user-card-pro {
            background: white; border-radius: 12px; padding: 15px;
            border-left: 6px solid #0E3255; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }

        /* --- 5. EL '+' (CLIP) INTEGRADO EN LA BARRA --- */
        div[data-testid="stChatInput"] {
            padding-left: 50px !important;
        }
        .stPopover {
            position: fixed !important;
            bottom: 40px !important;
            left: calc(10% + 20px) !important;
            z-index: 1001 !important;
        }
        .stPopover button { background: transparent !important; color: #0E3255 !important; border: none !important; }

        /* --- 6. BOTÓN X FLOTANTE (Animación corregida) --- */
        #btn-exit {
            position: fixed; bottom: 40px; left: 40px;
            width: 65px; height: 65px; background: #FF4B4B;
            border-radius: 50%; display: flex; align-items: center;
            justify-content: center; color: white; font-size: 35px;
            text-decoration: none; z-index: 1002;
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
            transition: 0.3s ease;
        }
        #btn-exit:hover { transform: scale(1.1) rotate(180deg); background: #E04141; }
        </style>
    """, unsafe_allow_html=True)
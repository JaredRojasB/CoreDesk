import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; }
        
        /* Limpieza de iconos basura */
        span[data-testid="stWidgetLabel"], [data-testid="stIconMaterial"] { display: none !important; }

        /* Tarjeta de Usuario */
        .user-card-pro {
            background: white; border-radius: 10px; padding: 15px;
            border-left: 6px solid #0E3255; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-top: 20px;
        }

        /* Input de Chat Fijo */
        div[data-testid="stChatInput"] {
            position: fixed !important; bottom: 30px !important;
            width: 80% !important; left: 50% !important;
            transform: translateX(-50%) !important;
            z-index: 999 !important;
            padding-left: 55px !important;
        }

        /* Clip (+) Azul dentro de la barra */
        .stPopover {
            position: fixed !important; bottom: 42px !important;
            left: calc(10% + 20px) !important; z-index: 1001 !important;
        }
        .stPopover button { background: transparent !important; color: #0E3255 !important; border: none !important; font-size: 25px !important; }

        /* Botón X Flotante */
        #finalizar-btn {
            position: fixed; bottom: 40px; left: 40px;
            width: 65px; height: 65px; background-color: #FF4B4B;
            border-radius: 50%; display: flex; align-items: center;
            justify-content: center; color: white !important; font-size: 35px;
            text-decoration: none; z-index: 1002;
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4); transition: 0.3s;
        }
        #finalizar-btn:hover { transform: scale(1.1) rotate(180deg); background: #e04141; }
        </style>
    """, unsafe_allow_html=True)
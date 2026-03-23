import streamlit as st

def aplicar_chat():
    st.markdown("""
        <style>
        /* Fondo Blanco y Limpieza */
        .stApp { background-color: #FFFFFF; }
        div[data-testid="stHeader"] { display: none; }

        /* HEADER FIJO */
        .custom-header {
            background-color: white;
            padding: 10px 20px;
            border-bottom: 2px solid #f0f2f6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* LOGO TAMAÑO REAL */
        .logo-img { height: 80px !important; }

        /* TARJETA DE USUARIO FORMAL */
        .user-card {
            background: white;
            border-radius: 10px;
            padding: 15px;
            border-left: 5px solid #0E3255;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }

        /* BOTÓN X FLOTANTE (FIJO ABAJO IZQUIERDA) */
        .floating-x {
            position: fixed;
            bottom: 30px;
            left: 30px;
            width: 60px;
            height: 60px;
            background-color: #FF4B4B;
            color: white !important;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
            font-weight: bold;
            text-decoration: none;
            z-index: 1000;
            box-shadow: 0 4px 10px rgba(255, 75, 75, 0.3);
            transition: 0.3s;
        }
        .floating-x:hover {
            transform: scale(1.1) rotate(90deg);
            background-color: #e04141;
        }

        /* AJUSTE BARRA DE CHAT */
        div[data-testid="stChatInput"] {
            border-radius: 15px !important;
        }
        </style>
    """, unsafe_allow_html=True)
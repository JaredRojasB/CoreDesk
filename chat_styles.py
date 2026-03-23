import streamlit as st

def aplicar_estilos_chat():
    """Estilos EXCLUSIVOS para la interfaz de chat activa"""
    st.markdown("""
        <style>
        /* ==========================================
           1. CABECERA FIJA Y LOGO (Izq)
           ========================================== */
        .header-fixed {
            position: fixed; top: 0; left: 0; width: 100%; height: 70px;
            background-color: white; z-index: 1000;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.03);
            display: flex; align-items: center; padding: 0 5%;
        }
        .logo-chat-legible {
            max-height: 50px;
            width: auto;
        }

        /* ==========================================
           2. TARJETA DE USUARIO FORMAL
           ========================================== */
        .main { padding-top: 100px; padding-bottom: 150px; } /* Padding para header y input */

        .user-card-formal {
            background-color: #ffffff;
            padding: 15px 25px;
            border-radius: 12px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
            border-left: 5px solid #0E3255;
            margin-bottom: 25px;
        }
        .user-card-title { color: #6c757d; font-size: 12px; margin-bottom: 5px; }
        .user-card-data { color: #0E3255; font-size: 16px; font-weight: 600; }

        /* ==========================================
           3. IDENTIDAD DE CHAT (Burbujas)
           ========================================== */
        .stChatMessage { 
            border-radius: 20px; 
            background-color: #fcfcfc;
            box-shadow: 0px 1px 4px rgba(0,0,0,0.02);
            margin-bottom: 12px;
        }

        /* ==========================================
           4. BARRA DE CHAT FIJA ABAJO CON EL CLIP INTEGRADO
           ========================================== */
        div[data-testid="stChatInput"] {
            position: fixed; bottom: 30px; z-index: 998;
            background-color: white; border-top: 1px solid #eee;
            padding: 10px 0; width: 85%;
            left: 50%; transform: translateX(-50%);
            border-radius: 15px; box-shadow: 0px -5px 15px rgba(0,0,0,0.03);
            padding-left: 60px !important; /* Espacio para el clip dentro */
        }

        /* El clip (Popover) LITERALMENTE dentro del input (al inicio) */
        button[data-testid="stBaseButton-headerNoPadding"] {
            position: absolute; left: 15px; top: 50%;
            transform: translateY(-50%);
            border-radius: 5px;
            background-color: transparent !important;
            color: #0E3255 !important; /* Azul como el botón de enviar */
            font-size: 20px !important;
            z-index: 1000;
        }

        /* ==========================================
           5. BOTÓN FLOTANTE 'X' (Inferior Izquierda)
           ========================================== */
        .floating-x-btn {
            position: fixed;
            bottom: 40px;
            left: 40px;
            width: 70px;
            height: 70px;
            background-color: #FF4B4B;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0px 5px 15px rgba(255, 75, 75, 0.4);
            cursor: pointer;
            z-index: 1001;
            transition: 0.3s ease;
            border: none;
        }
        
        /* La X enorme dentro del botón */
        .floating-x-btn::before {
            content: '×'; /* Carácter de multiplicación */
            color: white;
            font-size: 50px;
            font-weight: 300;
        }

        /* LEYENDA FLOTANTE AL PASAR EL MOUSE (Hover) */
        .floating-x-btn:hover::after {
            content: 'Finalizar chat';
            position: absolute;
            left: 80px;
            background-color: #333;
            color: white;
            padding: 5px 12px;
            border-radius: 5px;
            font-size: 14px;
            white-space: nowrap;
            opacity: 1;
            transition: opacity 0.3s;
        }

        .floating-x-btn:hover {
            transform: scale(1.1) rotate(90deg); /* Animación de giro */
            background-color: #e04141;
        }
        </style>
    """, unsafe_allow_html=True)
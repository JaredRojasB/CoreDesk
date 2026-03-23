import streamlit as st

def aplicar_estilos():
    st.markdown("""
        <style>
        /* ==========================================
           1. DISEÑO GLOBAL & FONDO
           ========================================== */
        .stApp { 
            background-color: #FFFFFF; 
        }

        /* Ocultamos elementos por defecto de Streamlit para limpieza total */
        div[data-testid="stHeader"] { display: none; }
        
        /* Tipografía responsiva */
        html { font-size: 16px; }
        @media (max-width: 768px) { html { font-size: 14px; } }

        /* ==========================================
           2. CABECERA FIJA (Header-Footer)
           ========================================== */
        .header-fixed {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 70px; /* Alto fijo profesional */
            background-color: white;
            z-index: 1000;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
            display: flex;
            align-items: center;
            justify-content: space-between; /* Logo izq, Botón der */
            padding: 0 5%;
        }

        /* Estilo del Logo PEQUEÑO (Izq) */
        .chat-logo-small {
            max-height: 50px; /* Tamaño responsivo y sutil */
            width: auto;
        }

        /* Botón Finalizar ROJO (Der) */
        button[kind="secondary"] {
            background-color: #FF4B4B !important;
            color: white !important;
            border: none !important;
            border-radius: 5px !important;
            font-weight: bold !important;
            padding: 0.5rem 1.2rem !important;
            font-size: 14px !important;
            transition: 0.3s;
        }
        button[kind="secondary"]:hover {
            background-color: #e04141 !important;
        }

        /* ==========================================
           3. APARTADO DE USUARIO & CHAT
           ========================================== */
        /* Agregamos padding al fondo de la app para no tapar los mensajes */
        .main {
            padding-top: 90px; /* Espacio para el header fijo */
            padding-bottom: 150px; /* Espacio para el input fijo */
        }

        /* Texto de usuario sutil, sin recuadros feos */
        .user-tag {
            color: #6c757d;
            font-size: 14px;
            margin-bottom: 20px;
            text-align: left;
        }

        /* Burbujas de chat limpias */
        .stChatMessage { 
            border-radius: 20px; 
            margin-bottom: 10px;
            box-shadow: 0px 1px 3px rgba(0,0,0,0.03);
        }

        /* ==========================================
           4. BARRA DE CHAT FIJA ABAJO
           ========================================== */
        div[data-testid="stChatInput"] {
            position: fixed;
            bottom: 30px;
            z-index: 999;
            background-color: white;
            border-top: 1px solid #ddd;
            padding: 10px 0;
            width: 80%; /* Ancho controlado */
            left: 50%;
            transform: translateX(-50%);
        }

        /* Botón '+' LITERALMENTE dentro del input (al inicio) */
        button[data-testid="stBaseButton-headerNoPadding"] {
            position: absolute;
            left: 10px;
            top: 50%;
            transform: translateY(-50%);
            border-radius: 5px;
            background-color: #f1f3f5 !important;
            color: #495057 !important;
            z-index: 1000;
        }

        /* Ajuste de padding del input de texto para el botón '+' */
        div[data-testid="stChatInput"] > div > textarea {
            padding-left: 50px !important;
        }
        </style>
    """, unsafe_allow_html=True)
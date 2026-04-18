import streamlit as st

def apply_custom_styles():
    """Aplica la paleta de colores con fondo verde opaco e inmunidad al modo oscuro"""
    st.markdown("""
        <style>
        /* 1. Forzar fondo verde opaco y color de texto base */
        /* Aplicamos a múltiples niveles para evitar que el modo oscuro lo rompa */
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background-color: #F4F7F0 !important; /* El verde opaco exacto */
            color: #2D3436 !important;
        }

        /* 2. Cabecera blanca para que resalte (igual que la app Oasis) */
        .header-box {
            background-color: #FFFFFF !important;
            padding: 35px;
            border-radius: 32px;
            box-shadow: 0 8px 30px rgba(149, 192, 106, 0.1);
            margin-bottom: 30px;
            border: 1px solid #E9EDDF;
            text-align: center;
        }

        /* 3. Tarjetas de métricas blancas con texto en gris oscuro y verde */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF !important;
            border-radius: 28px !important;
            padding: 25px !important;
            border: 1px solid #E9EDDF !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
        }

        /* Títulos de métricas en gris oscuro para que se distingan bien */
        div[data-testid="stMetricLabel"] > div > p {
            color: #4A4E4D !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase;
        }

        /* Números en verde Oasis */
        div[data-testid="stMetricValue"] > div {
            color: #95C06A !important;
            font-weight: 700 !important;
        }

        /* 4. Tabs Estilo Pastilla (Inmunes al modo oscuro) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px !important;
            background-color: transparent !important;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #E9EDDF !important;
            border-radius: 50px !important; /* Más redondeado como el botón Drink */
            color: #636E72 !important;
            border: none !important;
            padding: 8px 25px !important;
            transition: all 0.3s ease;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #95C06A !important;
            color: #FFFFFF !important;
        }

        /* 5. Asegurar que las tablas sean legibles sobre el fondo claro */
        .stDataFrame, div[data-testid="stTable"] {
            background-color: #FFFFFF !important;
            border-radius: 20px !important;
            padding: 10px;
        }

        /* 6. Forzar color de otros textos secundarios */
        p, span, h1, h2, h3 {
            color: #2D3436 !important;
        }
        </style>
        """, unsafe_allow_html=True)

def render_header(user_name):
    st.markdown(f"""
        <div class="header-box">
            <h1 style='margin:0; color:#2D3436 !important; font-size: 1.7rem;'>
                OASIS <span style='color:#95C06A !important;'>PET TRACKER</span>
            </h1>
            <p style='color:#636E72 !important; margin-top:5px;'>
                Análisis de Inventario • {user_name}
            </p>
        </div>
        """, unsafe_allow_html=True)
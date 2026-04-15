# main.py
import streamlit as st
import plotly.express as px
from datetime import datetime
import logic 
import style

# 1. Configuración de página y estilos
st.set_page_config(page_title="Petmedica Intel", layout="wide", page_icon="🐾")
style.apply_custom_styles()

# --- LÓGICA DE SESIÓN (LOGIN) ---
if 'auth' not in st.session_state: 
    st.session_state.auth = False

if not st.session_state.auth:
    with st.sidebar:
        st.markdown("### 🔐 Acceso Petmedica")
        u = st.text_input("Usuario (UPC o Vet)")
        p = st.text_input("Clave", type="password")
        if st.button("Ingresar", use_container_width=True):
            if u == "estudiante@upc.edu.pe" and p == "upc2026":
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    # --- 2. CARGA Y PROCESAMIENTO DE DATOS ---
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQatK31NMjLR7cXk3RejqLRdDV5Q7-GaGZ7c8_l79nIL_OoacChSSOTQ-ONAFNuKS1l9Lu2CXE25WXc/pub?gid=0&single=true&output=csv"
    
    try:
        data = logic.load_data(URL)
        ventas_df = logic.get_ventas_analisis(data)
        resumen_stock = logic.get_resumen_inventario(data)

        # --- 3. CABECERA ---
        style.render_header(st.session_state.user)
        
        # --- 4. TABS ---
        tab1, tab2, tab3 = st.tabs(["📊 Resumen", "🏷️ Análisis Categorías", "📅 Tendencias Mensuales"])

        # TAB 1: RESUMEN (Dashboard OASIS Fresco)
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Fila de métricas estilizadas como "paneles" de OASIS
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="INGRESOS TOTALES (S/.)", value=f"S/ {ventas_df['Monto'].sum():,.2f}")
            with col2:
                st.metric(label="VALOR NETO ALMACÉN", value=f"S/ {(resumen_stock['Cantidad'] * resumen_stock['Precio']).sum():,.2f}")
            with col3:
                st.metric(label="PRODUCTOS EN RIESGO", value=len(resumen_stock[resumen_stock['Cantidad'] < 5]))

            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # Sección de Gráficos Minimalistas
            c_left, c_right = st.columns([2, 1])
            
            with c_left:
                st.markdown("<p style='color:#636E72; font-weight:600; font-size:0.9rem;'>🔥 TOP VENTAS</p>", unsafe_allow_html=True)
                top4 = ventas_df.groupby('Nombre')['Cantidad'].sum().abs().nlargest(4).reset_index()
                
                # Gráfico Minimalista: Barra Verde Principal
                fig_top = px.bar(top4, x='Nombre', y='Cantidad', 
                                 color_discrete_sequence=['#95C06A'], # Verde OASIS
                                 text_auto=True, template="plotly_white")
                
                fig_top.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color="#636E72",
                    margin=dict(l=0, r=0, t=20, b=0),
                    xaxis=dict(showgrid=False, title=""),
                    yaxis=dict(showgrid=True, gridcolor='#F2F2F2', title="") # Grilla muy suave
                )
                st.plotly_chart(fig_top, use_container_width=True, config={'displayModeBar': False})
            
            with c_right:
                st.markdown("<p style='color:#636E72; font-weight:600; font-size:0.9rem;'>⚠️ ALERTAS STOCK</p>", unsafe_allow_html=True)
                # Dataframe más claro e integrado
                st.dataframe(resumen_stock[resumen_stock['Cantidad'] < 5][['Nombre', 'Cantidad']], 
                             use_container_width=True, hide_index=True)

        # TAB 2: ANÁLISIS DE CATEGORÍAS (Gráficos Monocromáticos)
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<p style='color:#636E72; font-weight:600; font-size:0.9rem;'>🏷️ VALOR DE INVENTARIO</p>", unsafe_allow_html=True)
                resumen_stock['Valor_Neto'] = resumen_stock['Cantidad'] * resumen_stock['Precio']
                # Donut Chart Minimalista (Gama de Verdes-Grises)
                fig_pie = px.pie(resumen_stock, values='Valor_Neto', names='Categoria', hole=0.7,
                                 color_discrete_sequence=['#95C06A', '#BDD9A2', '#DEE9CD', '#EEEEEE'],
                                 template="plotly_white")
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    font_color="#636E72",
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
            with c2:
                # Rotación por categoría
                st.write("Análisis de rotación aquí.")

        # TAB 3: TENDENCIAS MENSUALES
        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            pivot = logic.get_pivot_estacionalidad(ventas_df)
            if not pivot.empty:
                prod_sel = st.selectbox("Seleccionar item veterinario:", pivot.index)
                datos_p = pivot.loc[prod_sel].reset_index()
                datos_p.columns = ['Mes', 'Ventas']
                
                # Gráfico de líneas sutil con curva suave
                fig_est = px.line(datos_p, x='Mes', y='Ventas', markers=True, 
                                  color_discrete_sequence=['#95C06A'],
                                  line_shape='spline', # Curva suave
                                  template="plotly_white")
                fig_est.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font_color="#636E72",
                    xaxis=dict(showgrid=False, title=""), 
                    yaxis=dict(gridcolor='#F2F2F2', title="")
                )
                st.plotly_chart(fig_est, use_container_width=True, config={'displayModeBar': False})

        # SECCIÓN FINAL: BASE DE DATOS
        st.markdown("<br><hr style='border: 0.1px solid rgba(0,0,0,0.05)'><br>", unsafe_allow_html=True)
        with st.expander("📂 Base de datos de inventario completo"):
            st.dataframe(resumen_stock, use_container_width=True)

    except Exception as e:
        st.error(f"Error en la carga de datos: {e}")
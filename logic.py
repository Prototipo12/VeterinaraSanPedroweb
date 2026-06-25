import pandas as pd
import streamlit as st
import datetime
import numpy as np

def load_data(url):
    """
    Carga datos desde un CSV (o Google Sheets) y prepara las fechas.
    """
    try:
        # 1. Lee el archivo
        df = pd.read_csv(url)
        
        # 2. Limpia los datos
        if 'Nombre' in df.columns:
            df['Nombre'] = df['Nombre'].str.lower().str.strip()
        
        # 3. Procesamiento de Fechas
        # dayfirst=True evita errores de mes > 12
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
        
        # Elimina filas con fechas rotas (NaT) para que no crashee el gráfico
        df = df.dropna(subset=['Fecha'])
        
        # 4. Atributos
        df['Mes_Año'] = df['Fecha'].dt.to_period('M').astype(str)
        df['Semana'] = df['Fecha'].dt.isocalendar().week
        df['Mes_Num'] = df['Fecha'].dt.month
        df['Año'] = df['Fecha'].dt.year
        
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

def get_ventas_analisis(df):
    """
    Filtra las transacciones que son ventas. 
    Detecta por signo negativo y por etiqueta 'SALIDA'.
    """
    if df.empty: return df

    # Define la venta si la cantidad es negativa O si el tipo es SALIDA
    condicion_venta = (df['Cantidad'] < 0)
    if 'Tipo' in df.columns:
        condicion_venta = condicion_venta | (df['Tipo'].str.upper() == 'SALIDA')
    
    ventas = df[condicion_venta].copy()
    
    # Asegura que la cantidad para el cálculo sea positiva (valor absoluto)
    # y calculamos el Monto Total
    ventas['Monto'] = np.abs(ventas['Cantidad']) * ventas['Precio']
    
    return ventas

def get_ventas_temporales(ventas_df, periodo='mes'):
    """
    Filtra las ventas según el tiempo actual del sistema.
    """
    if ventas_df.empty: return ventas_df
    
    hoy = datetime.datetime.now()
    
    if periodo == 'mes':
        return ventas_df[(ventas_df['Mes_Num'] == hoy.month) & (ventas_df['Año'] == hoy.year)]
    
    elif periodo == 'semana':
        return ventas_df[ventas_df['Semana'] == hoy.isocalendar().week]
    
    return ventas_df

def get_pivot_estacionalidad(ventas_df):
    """
    Crea una matriz para la pestaña 'Tendencias'.
    """
    if ventas_df.empty:
        return pd.DataFrame()
        
    # Agrupamos por nombre y mes/año
    pivot = ventas_df.pivot_table(
        index='Nombre', 
        columns='Mes_Año', 
        values='Monto', 
        aggfunc='sum'
    ).fillna(0)
    
    return np.abs(pivot)
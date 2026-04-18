import pandas as pd

def load_data(url):
    """Carga datos y asegura que la fecha sea procesable"""
    df = pd.read_csv(url)
    # Convertimos Fecha a objeto datetime real
    if 'Nombre' in df.columns:
        df['Nombre'] = df['Nombre'].str.lower().str.strip()
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    # Creamos etiquetas de tiempo para filtros
    df['Mes_Año'] = df['Fecha'].dt.to_period('M').astype(str)
    df['Semana'] = df['Fecha'].dt.isocalendar().week
    df['Mes_Num'] = df['Fecha'].dt.month
    df['Año'] = df['Fecha'].dt.year
    return df

def get_ventas_analisis(df):
    """Filtra ventas (salidas) y calcula montos"""
    # Usamos la columna 'Tipo' o cantidad negativa
    ventas = df[df['Cantidad'] < 0].copy()
    ventas['Monto'] = ventas['Cantidad'].abs() * ventas['Precio']
    return ventas

def get_ventas_temporales(ventas_df, periodo='mes'):
    """Filtra ventas por el periodo actual (semana o mes)"""
    import datetime
    hoy = datetime.datetime.now()
    if periodo == 'mes':
        return ventas_df[(ventas_df['Mes_Num'] == hoy.month) & (ventas_df['Año'] == hoy.year)]
    elif periodo == 'semana':
        return ventas_df[ventas_df['Semana'] == hoy.isocalendar().week]
    return ventas_df

def get_pivot_estacionalidad(ventas_df):
    """Matriz de ventas mensuales por producto"""
    return ventas_df.pivot_table(index='Nombre', columns='Mes_Año', values='Monto', aggfunc='sum').fillna(0)
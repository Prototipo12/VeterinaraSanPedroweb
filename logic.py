import pandas as pd  #ENCARGADO DE LA MANIPULACION Y ANALISIS DE DATOS EN TABLAS
import streamlit as st  #INTERACTUA CON LA INTERFAZ GRAFICA DE USUARIO
import datetime  #ENCARGADO DE MANEJAR FECHAS Y HORAS
import numpy as np  #LIBRERIA PARA CALCULOS NUMERICOS Y OPERACIONES MATEMATICAS 
import requests  #PERMITE HACER PETICIONES HTTP DESDE PYTHON HACIA INTERNET
import json  #SIRVE PARA EMPAQUETAR DATOS EN FORMATO JSON 


# 1. EXCEPCIONES PERSONALIZADAS (Excepciones)

class ErrorDatoInvalido(Exception):  #CREA UNA NUEVA CLASE ERROR HEREDANDO DE LA CLASE BASE EXCEPTION DE PYTHON
    """Excepción lanzada cuando los datos de entrada no son válidos."""
    pass

class ErrorStockCritico(Exception):  #SE UTILIZA PARA ALERTAR CUANDO LOS PRODUCTOS LLEGAN A NIVELES BAJOS
    """Excepción lanzada cuando el stock alcanza niveles críticos."""
    pass

# GESTIÓN DE USUARIOS

class Usuario:
    """Clase base para representar a un usuario del sistema."""
    def __init__(self, id_usuario, username, password, role): #CONSTRUCTOR DE LA CLASE
        self.id_usuario = int(id_usuario) #CONVIERTE A UN NUMERO ENTERO
        self.username = str(username).strip().lower() #CONVIERTE EL NOMBRE A TEXTO QUITANDO LOS ESPACIOS VACIOS Y EN MINUSCULA
        self.password = str(password).strip()  #ALMACENA LA CONTRASEÑA LIMPIA
        self.role = str(role).strip().lower() # 'admin' o 'estudiante'

    def verificar_credenciales(self, user, pwd):  #COMPARA LOS DATOS INGRESADOS EN EL FORMULARIO DE INICIO DE SESION
        return self.username == str(user).strip().lower() and self.password == str(pwd).strip()#verifica las credenciales segun el app script


class GestorUsuarios:
    """Clase que administra la colección de usuarios conectada a Google Sheets y Apps Script."""
    def __init__(self, url_usuarios_sheets=None, url_apps_script=None): #EL CONSTRUCTOR RECIBE LAS DIRECCIONES WEB 
        self.url_sheets = url_usuarios_sheets
        self.url_apps_script = url_apps_script
        self.usuarios = [] #INICIALIZA UNA LISTA VACIA DONDE SE ALMACENAN LOS OBJETOS
        self.cargar_usuarios()  #LLAMA AUTOMATICAMENTE AL METODO CARGA APENAS SE CREA EL GESTOR

    def cargar_usuarios(self):  #ENCARGADO DE PROCESAR LOS USUARIOS DESDE LA NUBE
        """Carga los usuarios desde la fuente web pública de Google Sheets."""
        try:
            if self.url_sheets:  #VERIFICA SI SE PROPORCIONO UNA DIRECCION WEB DE GOOGLE SHEETS
                df_users = pd.read_csv(self.url_sheets)  #UTILIZA PANDAS PARA DESCARGAR EL ARCHIVO CSV PUBLICO Y CONVERTIRLO EN DATAFRAME
                self.usuarios = []
                for _, row in df_users.iterrows():  #RECORRE CADA FILA DE LA TABLA DE DATOS
                    self.usuarios.append(
                        Usuario(row['ID'], row['Usuario'], row['Clave'], row['Rol'])  #POR CADA FILA CREA UN OBJETO DE LA CLASE USUARIO PASANDOLE LOS DATOS DE LA COLUMNA
                    )
            else:
                raise Exception("Sin URL")  #SI NO HAY URL LANZA UN ERROR INTENCIONALMENTE PARA ACTIVAR EL RESPALDO
        except Exception as e:
            # Respaldo por defecto si falla la red
            self.usuarios = [
                Usuario(1, "UserAdmin", "adminVet1", "admin"),
                Usuario(2, "Userprac", "practicante2026", "estudiante")
            ]

    def autenticar(self, username, password):  #ENCARGADO DE VALIDAR LAS CREDENCIALES DE ACCESO
        """Verifica las credenciales del usuario."""
        for user_obj in self.usuarios:  #RECORRE LA LISTA DE LOS OBJETOS DE USUARIOS CARGADOS
            if user_obj.verificar_credenciales(username, password):
                return user_obj.role  #LLAMA AL METODO DE CLASE USUARIO PARA COMPROBAR SI COINCIDEN, SI ES CORRECTO DEVUELVE EL ROL DEL USUARIO 
        return None  #SI TERMINA EL CICLO Y NINGUN USUARIO COINCIDE, DEVUELVE NADA INDICANDO QUE EL ACCESO ES DENEGADO

    def registrar_practicante(self, username, password): #METODO QUE PERMITE DAR DE ALTA A UN NUEVO ESTUDIANTE
        """Registra un nuevo practicante enviándolo a Google Apps Script para que se guarde en el Sheet."""
        username_limpio = str(username).strip().lower() #LIMPIA ESPACIOS Y PASA EL NOMBRE A MINUSCULAS
        
        for user_obj in self.usuarios:
            if user_obj.username == username_limpio:
                raise ErrorDatoInvalido("El nombre de usuario ya existe en el sistema.") #RECORRE LA LISTA DE USUARIOS Y SI ENCUENTRA UNO CON EL MISMO NOMBRE LANZA LA EXCEPCION PERSONALIZADA
        
        if not username or not password:
            raise ErrorDatoInvalido("El usuario y la contraseña no pueden estar vacíos.")

        # Estructura de datos para el Apps Script
        payload = {  #CREA UN DICCIONARIO EN FORMATO DE DATOS QUE CONTIENE LA ACCION, EL USUARIO, LA CONTRASEÑA Y EL ROL PARA ENVIARLO A APPS SCRIPT
            "action": "registrar_usuario",
            "username": username_limpio,
            "password": str(password).strip(),
            "role": "estudiante"
        }

        try:
            if self.url_apps_script:  #VERIFICA QUE LA DIRECCION WEB DEL APPS SCRIPT ESTE DEBIDAMENTE CONFIGURADA ANTES DE INTENTAR LA CONEXION 
                # esto envia la petición POST al Apps Script
                response = requests.post(self.url_apps_script, json=payload)  #UTILIZA LA LIBRERIA PARA ENVIAR UNA PETICION HTTP DE TIPO POST ENVIANDO EL PAYLOAD EMPAQUETADO COMO JSON
                resultado = response.json()
                
                if resultado.get("status") == "success":  #COMPRUEBA SI EL SERVIDOR CONFIRMO QUE EL REGISTRO SE REALIZO CORRECTAMENTE EN LA HOJA DE CALCULO
                    # Recarga la lista desde Sheets para traer el nuevo usuario registrado
                    self.cargar_usuarios()
                    return True
                else:
                    raise Exception("Error en el servidor de Apps Script.")
            else:
                raise Exception("Falta configurar la URL de Apps Script.")
        except Exception as err:
            raise ErrorDatoInvalido(f"No se pudo guardar en Google Sheets: {err}")

# 2. CLASES, HERENCIA Y POLIMORFISMO

class Producto:
    """Clase base que representa un producto general de la veterinaria."""
    def __init__(self, nombre, categoria, precio, cantidad):
        self.nombre = str(nombre).lower().strip()
        self.categoria = str(categoria).strip()
        
        # Control de excepciones en atributos numéricos
        try:
            self.precio = float(precio)
            self.cantidad = int(cantidad)
            if self.precio < 0 or self.cantidad < 0:
                raise ErrorDatoInvalido("El precio y la cantidad no pueden ser negativos.")
        except ValueError:
            raise ErrorDatoInvalido("Precio o cantidad deben ser valores numéricos válidos.")

    def evaluar_alerta(self):
        """Método base para evaluar alertas de stock (Polimorfismo)."""
        return self.cantidad < 5

    def obtener_detalles(self):
        return f"Producto: {self.nombre} | Categoría: {self.categoria} | Stock: {self.cantidad}"


class ProductoFarmaceutico(Producto):
    """Clase derivada (Herencia) para productos de farmacia/medicamentos."""
    def __init__(self, nombre, categoria, precio, cantidad, requiere_receta=True):
        super().__init__(nombre, categoria, precio, cantidad)
        self.requiere_receta = requiere_receta

    # Polimorfismo: Sobrescribe la evaluación de alerta (ej: stock crítico más estricto para fármacos)
    def evaluar_alerta(self):
        return self.cantidad < 10

    def obtener_detalles(self):
        receta_txt = "Sí" if self.requiere_receta else "No"
        return f"[FARMACIA] {super().obtener_detalles()} | Receta: {receta_txt}"


class ProductoAccesorio(Producto):
    """Clase derivada (Herencia) para accesorios y juguetes."""
    def __init__(self, nombre, categoria, precio, cantidad, material="Estándar"):
        super().__init__(nombre, categoria, precio, cantidad)
        self.material = material

    # Polimorfismo
    def evaluar_alerta(self):
        return self.cantidad < 3

    def obtener_detalles(self):
        return f"[ACCESORIO] {super().obtener_detalles()} | Material: {self.material}"


class GestorInventario:
    """Clase que gestiona la relación entre múltiples productos y transacciones (Relación de Asociación)."""
    def __init__(self):
        self.productos = []

    def agregar_producto(self, producto: Producto):
        if not isinstance(producto, Producto):
            raise ErrorDatoInvalido("El objeto debe ser una instancia de la clase Producto.")
        self.productos.append(producto)

    def obtener_total_inventario(self):
        return sum(p.precio * p.cantidad for p in self.productos)


# 3. FUNCIONES DE APOYO PARA STREAMLIT

def load_data(url):
    """
    Carga datos desde un CSV (o Google Sheets) y prepara las fechas.
    Manejo de excepciones integrado.
    """
    try:
        df = pd.read_csv(url)
        
        if 'Nombre' in df.columns:
            df['Nombre'] = df['Nombre'].str.lower().str.strip()
        
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Fecha'])
        
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

    condicion_venta = (df['Cantidad'] < 0)
    if 'Tipo' in df.columns:
        condicion_venta = condicion_venta | (df['Tipo'].str.upper() == 'SALIDA')
    
    ventas = df[condicion_venta].copy()
    ventas['Monto'] = np.abs(ventas['Cantidad']) * ventas['Precio']
    
    return ventas

def get_ventas_temporales(ventas_df, periodo='mes'):
    if ventas_df.empty: return ventas_df
    hoy = datetime.datetime.now()
    
    if periodo == 'mes':
        return ventas_df[(ventas_df['Mes_Num'] == hoy.month) & (ventas_df['Año'] == hoy.year)]
    elif periodo == 'semana':
        return ventas_df[ventas_df['Semana'] == hoy.isocalendar().week]
    
    return ventas_df

def get_pivot_estacionalidad(ventas_df):
    if ventas_df.empty:
        return pd.DataFrame()
        
    pivot = ventas_df.pivot_table(
        index='Nombre', 
        columns='Mes_Año', 
        values='Monto', 
        aggfunc='sum'
    ).fillna(0)
    
    return np.abs(pivot)
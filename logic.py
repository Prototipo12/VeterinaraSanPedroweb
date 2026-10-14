import pandas as pd #ENCARGADO DE LA MANIPULACION Y ANALISIS DE DATOS EN TABLAS
import streamlit as st #INTERACTUA CON LA INTERFAZ GRAFICA DE USUARIO
import datetime #ENCARGADO DE MANEJAR FECHAS Y HORAS
import numpy as np #LIBRERIA PARA CALCULOS NUMERICOS Y OPERACIONES MATEMATICAS
import requests #PERMITE HACER PETICIONES HTTP DESDE PYTHON HACIA INTERNET
import json #SIRVE PARA EMPAQUETAR DATOS EN FORMATO JSON 


# EXCEPCIONES PERSONALIZADAS (Excepciones)

class ErrorDatoInvalido(Exception): #CREA UNA NUEVA CLASE ERROR HEREDANDO DE LA CLASE BASE EXCEPTION DE PYTHON
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
        self.username = str(username).strip().lower() #CONVIERTE EL NOMBRE A TEXTO QUITANDO LOS ESPACIOS VACIOS Y EN MINUSCUL
        self.password = str(password).strip() #ALMACENA LA CONTRASEÑA LIMPIA
        self.role = str(role).strip().lower() # 'admin' o 'estudiante'

    def verificar_credenciales(self, user, pwd): #COMPARA LOS DATOS INGRESADOS EN EL FORMULARIO DE INICIO DE SESION
        return self.username == str(user).strip().lower() and self.password == str(pwd).strip() #verifica las credenciales segun el app script


class GestorUsuarios: #DEFINE LA CLASE GESTORA QUE CONTENDRA UNA COLECCION DE OBJETOS DE TIPO usuario
    """Clase que administra la colección de usuarios conectada a Google Sheets y Apps Script."""
    def __init__(self, url_usuarios_sheets=None, url_apps_script=None):
        self.url_sheets = url_usuarios_sheets
        self.url_apps_script = url_apps_script
        self.usuarios = [] #INICIALIZA UNA LISTA VACIA DONDE SE ALMACENAN LOS OBJETOS
        self.cargar_usuarios() #LLAMA AUTOMATICAMENTE AL METODO CARGA APENAS SE CREA EL GESTOR

    def cargar_usuarios(self): #ENCARGADO DE PROCESAR LOS USUARIOS DESDE LA NUBE
        """Carga los usuarios desde Google Sheets manteniendo siempre al administrador por defecto."""
        admin_por_defecto = Usuario(1, "UserAdmin", "adminVet1", "admin")
        self.usuarios = [admin_por_defecto]
        
        try:     
            if self.url_sheets:
                df_users = pd.read_csv(self.url_sheets)
                for _, row in df_users.iterrows():
                    username_sheet = str(row['Usuario']).strip().lower()
                    if username_sheet != "useradmin":
                        self.usuarios.append(
                            Usuario(row['ID'], row['Usuario'], row['Clave'], row['Rol'])
                        )
            else:
                raise Exception("Sin URL")
        except Exception as e:
            practicante_respaldo = Usuario(2, "Userprac", "practicante2026", "estudiante")
            if not any(u.username == "userprac" for u in self.usuarios):
                self.usuarios.append(practicante_respaldo)

    def autenticar(self, username, password):  #ENCARGADO DE VALIDAR LAS CREDENCIALES DE ACCESO
        """Verifica las credenciales recargando primero los datos para reflejar cambios en tiempo real."""
        # Forzamos una recarga rápida de la base de datos para que detecte si borraron o agregaron usuarios en Sheets
        self.cargar_usuarios()
        
        username_limpio = str(username).strip().lower()
        password_limpio = str(password).strip()
        
        for user_obj in self.usuarios:  #RECORRE LA LISTA DE TODOS LOS OBJETOS USUARIOS CARGADOS 
            if user_obj.username == username_limpio and user_obj.password == password_limpio: #LLAMA AL METODO DE LA CLASE usuario PARA COMPROBAR SI COINCIDEN 
                return user_obj.role
        return None  #SI TERMINA EL CICLO Y NINGUN USUARIO COINCIDE, DEVUELE NONE INDICANDO QUE ES DENEGADO

    def registrar_practicante(self, username, password):  #METODO QUE PERMITE DAR DE ALTA A UN NUEVO ESTUDIANTE O PRACTICANTE 
        """Registra un nuevo practicante enviándolo a Google Apps Script y actualizando la memoria local."""
        username_limpio = str(username).strip().lower()  #LIMPIA LOS ESPACIOS Y PASA EL NOMBRE A MINUSCULAS
        
        for user_obj in self.usuarios:
            if user_obj.username == username_limpio:
                raise ErrorDatoInvalido("El nombre de usuario ya existe en el sistema.") #SI LOS CAMPOS ESTAN EN BLANCO, LANZA LA EXCEPCION
        
        if not username or not password:
            raise ErrorDatoInvalido("El usuario y la contraseña no pueden estar vacíos.")

        payload = {  #CREA UN DICCIONARIO EN FORMATO DE DATOS
            "action": "registrar_usuario",
            "username": username_limpio,
            "password": str(password).strip(),
            "role": "estudiante"
        }

        try:  #IMPLEMENTA UNA ESTRUCTURA DE CONTROL DE ERRORES PARA MANEJAR FALLOS DE RED
            if self.url_apps_script:  #VERIFICA QUE LA DIRECCION WEB DEL APPS SCRIPT ESTE DEBIDAMENTE CONFIGURADA
                response = requests.post(self.url_apps_script, json=payload)  #UTILIZA LA LIBRERIA requests PARA ENVIAR UNA PETICION HTTP DE TIPO POST ENVIANDO EL PAYLOAD EMPAQUETADO COMO JSON
                resultado = response.json()  #CONVIERTE LA RESPUESTA OBTENIDA DEL SERVIDOR WEB EN UN DICCIONARIO DE PYTHON 
                
                if resultado.get("status") == "success":  #COMPRUEBA SI EL SERVIDOR CONFIRMO QUE EL REGISTRO SE REALIZO CORRECTAMENTE EN LA HOJA DE CALCULO 
                    nuevo_id = len(self.usuarios) + 1  
                    nuevo_usuario = Usuario(nuevo_id, username_limpio, password, "estudiante")
                    self.usuarios.append(nuevo_usuario)  #VUELVE A INVOCAR EL METODO DE CARGA PARA ACTUALIZAR LA LISTA LOCAL DE USUARIOS TRAYENDO EL NUEVO REGISTRO DIRECTAMENTE DESDE GOOGLE SHEETS
                    return True
                else:
                    raise Exception("Error en el servidor de Apps Script.")
            else:
                raise Exception("Falta configurar la URL de Apps Script.")  
        except Exception as err:
            raise ErrorDatoInvalido(f"No se pudo guardar en Google Sheets: {err}")  #CAPTURA CUALQUIER ERROR IMPREVISTO DE RED O DEL SERVIDOR Y LO TRANSFORMA EN LA EXCEPCION PERSONALIZADA 

# 2. CLASES, HERENCIA Y POLIMORFISMO

class Producto:  #DEFINE LA CLASE PRINCIPAL QUE AGRUPA LOS ATRIBUTOS 
    """Clase base que representa un producto general de la veterinaria."""
    def __init__(self, nombre, categoria, precio, cantidad):  #EL CONSTRUCTOR QUE INICIALIZA LOS DATOS BASICOS DEL PRODUCTO
        self.nombre = str(nombre).lower().strip()
        self.categoria = str(categoria).strip()  #GUARDAN EL TEXTO LIMPIO DE ESPACIOS Y ESTANDARIZAN EL NOMBRE EN MINUSCULAS
        
        # Control de excepciones en atributos numéricos
        try:
            self.precio = float(precio)  #INTENTAN CONVERTIR LOS VALORES DE ENTRADA A TIPO NUMERICO DECIMAL Y ENTERO RESPECTIVAMENTE
            self.cantidad = int(cantidad)
            if self.precio < 0 or self.cantidad < 0:  #VALIDA QUE NO SE INGRESEN NUMEROS NEGATIVOS, LANZANDO LA EXCEPCION PERSONALIZADA 
                raise ErrorDatoInvalido("El precio y la cantidad no pueden ser negativos.")  
        except ValueError:  #CAPTURA ERRORES SI EL USUARIO INGRESA LETRAS O SIMBOLOS EN LUGAR DE NUMEROS EN LOS CAMPOS DE PRECIO O CANTIDAD
            raise ErrorDatoInvalido("Precio o cantidad deben ser valores numéricos válidos.")

    def evaluar_alerta(self):  #METODO BASE DISEÑADO PARA EL POLIMORFISMO
        """Método base para evaluar alertas de stock (Polimorfismo)."""
        return self.cantidad < 5  

    def obtener_detalles(self):  #METODO QUE RETORNA UNA CADENA DE TEXTO FORMATEADA CON LOS DATOS PRINCIPALES DEL PRODUCTO
        return f"Producto: {self.nombre} | Categoría: {self.categoria} | Stock: {self.cantidad}"


class ProductoFarmaceutico(Producto):  #DEFINE UNA NUEVA CLASE QUE HEREDA DE LA CLASE PADRE 
    """Clase derivada (Herencia) para productos de farmacia/medicamentos.""" 
    def __init__(self, nombre, categoria, precio, cantidad, requiere_receta=True):  #CONTRUCTOR DE LA CLASE HIJA. RECIBE LOS PARAMETROS GENERALES MAS UNO NUEVO EXCLUSIVO 
        super().__init__(nombre, categoria, precio, cantidad)  #UTILIZA SUPER() PARA LLAMAR AL CONSTRUCTOR DE LA CLASE PADRE (PRODUCTO), REUTILIZANDO LA LOGICA DE INICIALIZACION 
        self.requiere_receta = requiere_receta  #INICIALIZA EL ATRIBUTO EXCLUSIVO QUE INDICA SI EL MEDICAMENTO NECESITA RECETA MEDICA

    # Polimorfismo: Sobrescribe la evaluación de alerta (ej: stock crítico más estricto para fármacos)
    def evaluar_alerta(self):  #DEMOSTRACION CLARA DE POLIMORFISMO Y SOBRESCRITURA  
        return self.cantidad < 10

    def obtener_detalles(self):  #SOBRESCRIBE EL METODO DE DETALLES
        receta_txt = "Sí" if self.requiere_receta else "No"
        return f"[FARMACIA] {super().obtener_detalles()} | Receta: {receta_txt}"  #REUTILIZA EL TEXTO BASE DEL PADRE USANDO SUPER() Y LE CONCATENA EL ESTADO DE LA RECETA


class ProductoAccesorio(Producto):  #DEFINE UNA SEGUNDA CLASE HIJA QUE HEREDA DE LA CLASE BASE PRODUCTO, ESPECIALIZANDOSE AHORA EN ARTICULOS COMO ACCESORIOS
    """Clase derivada (Herencia) para accesorios y juguetes."""
    def __init__(self, nombre, categoria, precio, cantidad, material="Estándar"):  #EL CONSTRUCTOR RECIBE LOS PARAMETROS GENERALES MAS UN ATRIBUTO UNICO LLAMADO material
        super().__init__(nombre, categoria, precio, cantidad)
        self.material = material  #ASIGNA EL VALOR DEL MATERIAL RECIBIDO COMO UN ATRIBUTO EXCLUSIVO

    # Polimorfismo
    def evaluar_alerta(self):  #APLICA POLIMORFISMO PARA LOS ACCESORIOS, LA ALERTA DE STOCK CRITICO SE DISPARA CUANDO LA CANTIDAD ES MENOR A 3
        return self.cantidad < 3

    def obtener_detalles(self):  #SOBRESCRIBE EL METODO DE VISUALIZACION
        return f"[ACCESORIO] {super().obtener_detalles()} | Material: {self.material}"

#ENCARGADO DE ADMINISTRAR LA COLECCION DE MULTIPLES PRODUCTOS APLICANDO EL PRINCIPIO DE ASOCIACION
class GestorInventario: #DEFINE LA CLASE GESTORA QUE CENTRALIZA LAS OPERACIONES SOBRE TODOS LOS ARTICULOS DE LA VETERINARIA 
    """Clase que gestiona la relación entre múltiples productos y transacciones (Relación de Asociación)."""
    def __init__(self):  #CONSTRUCTOR
        self.productos = [] #SE GUARDARAN TODAS LAS INSTANCIAS DE LA CLASE PRODUCTO

    def agregar_producto(self, producto: Producto): #METODO PARA AÑADIR UN NUEVO PRODUCTO AL INVENTARIO
        if not isinstance(producto, Producto):  #VALIDA MEDIANTE TIPADO Y ISINSTANCE QUE EL ELEMENTO INGRESADO PERTENEZCA REALMENTE A LA CLASE producto 
            raise ErrorDatoInvalido("El objeto debe ser una instancia de la clase Producto.") #LANZA LA EXCEPCION PERSONALIZADA
        self.productos.append(producto) #SI ES CORRECTO, AÑADE EL OBJETO A LA LISTA DE PRODUCTOS

    def obtener_total_inventario(self): #METODO DE CALCULO FINANCIERO
        return sum(p.precio * p.cantidad for p in self.productos) #RECORRE TODA LA LISTA OBTENIENDO EL VALOR ECONOMICO TOTAL DEL INVENTARIO 


# 3. FUNCIONES DE APOYO PARA STREAMLIT

#PARTE DE LAS HERRAMIENTAS DE APOYO PARA PROCESAR Y PREPARAR LOS DATOS QUE SE VISUALIZAN EN LA INTERFAZ DE STREAMLIT

def load_data(url): #DEFINE UNA FUNCION QUE RECIBE LA URL DE UN ARCHIVO CSV PARA CARGARLO
    """
    Carga datos desde un CSV (o Google Sheets) y prepara las fechas.
    Manejo de excepciones integrado.
    """
    try:
        df = pd.read_csv(url)  #UTILIZA LA LIBRERIA PANDAS PARA LEER EL ARCHIVO REMOTO Y CONVERTIRLO EN UN DATAFRAME
        
        if 'Nombre' in df.columns:  #COMPRUEBA SI EXISTE LA COLUMNA "NOMBRE"
            df['Nombre'] = df['Nombre'].str.lower().str.strip()  #LIMPIA LOS ESPACIOS SOBRANTES Y CONVIERTE TODO EL TEXTO A MINUSCULAS PARA EVITAR DUPLICADOS POR FORMATO
        
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')  #CONVIERTE LA COLUMNA DE TEXTO DE FECHA EN UN FORMATO DE FECHA REAL DE PYTHON
        df = df.dropna(subset=['Fecha'])  #ELIMINA CUALQUIER FILA QUE NO TENGA FECHA VALIDA
        
        df['Mes_Año'] = df['Fecha'].dt.to_period('M').astype(str)  #CREA UNA COLUMNA AGRUPADA POR MES Y AÑO
        df['Semana'] = df['Fecha'].dt.isocalendar().week  #EXTRAE EL NUMERO DE LA SEMANA DEL AÑO
        df['Mes_Num'] = df['Fecha'].dt.month  #EXTRAEN DE MANERA INDEPENDIENTE EL NUMERO DEL MES Y AÑO
        df['Año'] = df['Fecha'].dt.year
        
        return df  #DEVUELVE EL DATAFRAME COMPLETAMENTE LIMPIO Y ENRIQUECIDO CON LAS NUEVAS COLUMNAS CALCULADAS 
    except Exception as e:  #BLOQUEO DE MANEJO DE ERRORES, SI LA CARGA FALLA EL SISTEMA ATRAPA EL ERROR SIN ROMPERSE
        st.error(f"Error cargando datos: {e}")  #SI OCURRE UNA FALLA, MUESTRA UN MENSAJE DE ERROR EN LA INTERFAZ DE STREAMLIT
        return pd.DataFrame()  #DEVUELVE UNA TABLA VACIA PARA EVITAR QUE LA APLICACION WEB COLAPSE

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


def get_ventas_temporales(ventas_df, periodo='mes'):  #ENCARGADO DE FILTRAR LAS TRANSACCIONES DE VENTAS PARA ANALIZARLAS SEGUN UN PERIODO TEMPORAL ESPECIFICO
    if ventas_df.empty: return ventas_df  #COMPRUEBA SI EL DATAFRAME ESTA VACIO, DE SER ASI LO DEVUELVE AL INSTANTE PARA PREVENIR ERROR DE PROCESAMIENTO
    hoy = datetime.datetime.now()  #UTILIZA LA LIBRERIA datetime PARA CAPTURAR LA FECHA Y HORA DEL SISTEMA
    
    if periodo == 'mes':
        return ventas_df[(ventas_df['Mes_Num'] == hoy.month) & (ventas_df['Año'] == hoy.year)]  #FILTRA Y DEVUELVE UNICAMENTE LOS REGISTROS DONDE EL NUMERO DEL MES Y AÑO COINCIDAN CON LOS ACTUALES
    elif periodo == 'semana':
        return ventas_df[ventas_df['Semana'] == hoy.isocalendar().week]  #FILTRA LA TABLA PARA CONSERVAR EXCLUSIVAMENTE LAS TRANSACCIONES QUE OCURRIERON EN LA SEMANA ACTUAL USANDO EL ESTANDAR DEL CALENDARIO ISO
    
    return ventas_df  #SI NO COINCIDE, DEVUELVE EL DATAFRAME COMPLETO SIN APLICAR FILTROS DE TIEMPO

def get_pivot_estacionalidad(ventas_df):  #LA CUAL UTILIZA UNA TABLA DINAMICA DE PANDAS PARA ORGANIZAR Y ANALIZAR EL COMPORTAMIENTO DE LAS VENTAS A LO LARGO DEL TIEMPO
    if ventas_df.empty:
        return pd.DataFrame()  #VERIFICA SI LA TABLA DE VENTAS ESTA VACIA, SI NO HAY DATOS DEVUEVE UN DATAFRAME VACIO PARA EVITAR INTERRUPCIONES EN LA APLICACION
        
    pivot = ventas_df.pivot_table(  #CREA LA TABLA
        index='Nombre',   #UTILIZA EL NOMBRE DE CADA PRODUCTO COMO FILA DE TABLA
        columns='Mes_Año',   #COLOCA LOS PERIODOS DE TIEMPO COMO COLUMNA DE TABLA
        values='Monto',   #RELLENA LOS DATOS INTERNOS DE LA TABLA CON LOS MONTOS ECONOMICOS DE LAS VENTAS
        aggfunc='sum'  #APLICA LA FUNCION DE SUMA PARA TOTALIZAR LAS VENTAS DE UN MISMO PRODUCTO EN UN MISMO MES
    ).fillna(0)  #REEMPLAZA CUALQUIER ESPACIO O VALOR NULO POR UN 0, ASEGURANDO QUE NO QUEDEN CELDAS VACIAS
    
    return np.abs(pivot)  #DEVUELVE LA TABLA DINAMICA APLICANDO EL VALOR ABSOLUTO PARA GARANTIZAR QUE TODAS LAS CIFRAS MONETARIAS SEAN POSITIVO
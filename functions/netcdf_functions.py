# Funciones para la manipulacion del archivo netcdf
#
#
# Refs:
#   http://unidata.github.io/netcdf4-python/
#   http://flask.pocoo.org/docs/0.12/
#   netcdf date to datetime:
#       http://forum.marine.copernicus.eu/discussion/428/how-to-convert-netcdf-time-to-python-datetime-resolved/p1
#   Masked array:
#       https://docs.scipy.org/doc/numpy-1.13.0/reference/maskedarray.baseclass.html
#
#
# Posicion geo. para realizar pruebas:
#   -31.6265705,-60.7324942

from netCDF4 import Dataset, num2date
from pprint import pprint
import json
import datetime


#------------------------------------------------------------------------------------------------------------------
# Verifica ciertas condiciones necesarias para el correcto funcionamiento del servicio web.
#
# Diccionarios en Python
# https://docs.python.org/2/tutorial/datastructures.html#dictionaries
def check_estado():
    archivo = get_archivo_datos()
    estado = {
        'archivo': archivo['nombre'],
        'errores': [],
        'estado': 'OK',
        'vers_archivo_datos' : get_version_archivo_datos(),
        'msg': "Para poder realizar consultas el estado del servicio debe ser OK."
    }

    # Abrir archivo:
    fileHandler = abrir_archivo_datos()

    errores = []
    if fileHandler == False:
        errores.append(
            "Error al intentar abrir el archivo de datos. Este error se debe a que no se pudo encontrar el archivo u el mismo posee algun error.")
    else:
        variables = fileHandler.variables

        # Muestro nombres de variables y los guardo en una lista:
        lista_nombres = []
        for nombre in variables:
            lista_nombres.append(nombre)

        estado['variables'] = lista_nombres

    estado['errores'] = errores

    if len(errores) > 0:
        estado['estado'] = 'NOT_OK'

    return estado


# ------------------------------------------------------------------------------------------------------------------
# Devuelve informacion del archivo utilizado
def get_archivo_datos():
    file = 'wrf_20170823_full.nc'
    # dev:
    # return {'nombre': file, 'ruta': "../files/" + file}
    # prod:
    return {'nombre': file, 'ruta': "files/" + file}


# ------------------------------------------------------------------------------------------------------------------
# Permite abrir un archivo de datos
def abrir_archivo_datos():
    archivo = get_archivo_datos()
    try:
        fileHandler = Dataset(archivo['ruta'], "r", format="NETCDF4")
        return fileHandler
    except IOError:
        pass
    return False


# ------------------------------------------------------------------------------------------------------------------
# Muestra las variables meteorologicas definidas en el archivo.
def get_variables():
    fileHandler = abrir_archivo_datos()
    if fileHandler <> False:
        return fileHandler.variables.keys()
    return False


# ------------------------------------------------------------------------------------------------------------------
# Muestra las dimensiones definidas en el archivo.
def get_dimensiones():
    fileHandler = abrir_archivo_datos()
    if fileHandler <> False:
        return fileHandler.dimensions.keys()
    return False


# ------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------------------------
# Obtener
def variable_valores(variable):
    fileHandler = abrir_archivo_datos()
    if fileHandler <> False:
        variableMet = fileHandler.variables[variable];
        res = str(len(variableMet))
        return res
    return False


# ------------------------------------------------------------------------------------------------------------------
# Devuelve todos los valores correspondiente a la variable 'time' definidos como fechas en el formato datetime
def get_times():
    fileHandler = abrir_archivo_datos()
    if fileHandler == False:
        time = fileHandler.variables['time']
        times = time[:]
        t_unit = time.units # u'hours since 2017-08-23 00:00:00'
        t_cal = time.calendar
        tvalue = num2date(times, units = t_unit, calendar = t_cal)
        return tvalue
    return False

# ------------------------------------------------------------------------------------------------------------------
# Devuelve las coordenadas correspondiente al limite inferior-izquierdo(SO) y superior-derecho (NE). Estos puntos
# permiten delimitar la zona en donde se disponen valores. Por fuera de este rectangulo el modelo no calcula valores
# mientras que por dentro se encuentran los valores pronosticados. Dentro del rectangulo pueden existir coordenadas
# sin un valor asociado, esto se debe a que la zona pronosticada tiene forma de abanico.
def get_limites_rect():
    fileHandler = abrir_archivo_datos()
    if fileHandler <> False:
        lon = fileHandler.variables['lon']
        lat = fileHandler.variables['lat']
        limites = {
            'esq_suroeste' : { 'longitud' : min(lon), 'latitud' : min(lat) },
            'esq_noreste' : { 'longitud' : max(lon), 'latitud' : max(lat) }
        }
        return limites
    return False

# ------------------------------------------------------------------------------------------------------------------
# Verifica que una coordenada pasada como parametro se encuentre dentro del limite rectangular
def is_dentro(lat, lng):
    fileHandler = abrir_archivo_datos()
    if fileHandler <> False:
        lons = fileHandler.variables['lon']
        lats = fileHandler.variables['lat']
        lon_is_in = lng >= min(lons) and lng <= max(lons)
        lat_is_in = lat >= min(lats) and lng <= max(lats)
        return int(lon_is_in and lat_is_in)
    return None

def is_fuera(lat, lng):
    return not is_dentro(lat, lng)


# ------------------------------------------------------------------------------------------------------------------
# 

# ------------------------------------------------------------------------------------------------------------------
# Devuelve la version del archivo de datos en el formato YYYYMMDD
def get_version_archivo_datos( asDatetime = False ):
    fileHandler = abrir_archivo_datos()
    if fileHandler <> False:
        time = fileHandler.variables['time']
        t_unit = time.units  # u'hours since 2017-08-23 00:00:00'
        t_cal = time.calendar
        fecha = num2date(time[0], units=t_unit, calendar=t_cal)
        if asDatetime == True:
            return fecha
        else:
            return fecha.date().strftime("%Y%m%d")
    return False


# ------------------------------------------------------------------------------------------------------------------
# Devuelve la version del archivo de datos en el formato YYYYMMDD
def get_lat_long():
    fileHandler = abrir_archivo_datos()
    if fileHandler <> False:
        lat = fileHandler.variables['lat'];
        lon = fileHandler.variables['lon'];
        result = {
            'latitudes' : lat[:].tolist(),
            'longitudes' : lon[:].tolist()
        };
        return result

    return False

file = abrir_archivo_datos()
if file <> False:
    #pprint(vars(file.dimensions))
    #pprint(file.dimensions)
    temp = file.variables['temperature'];
    pprint(temp.size)
    #pprint(temp.units)
    pprint(temp[0].size)
    pprint(temp[0][0].size)
    pprint(temp[0][0][0].size)
    pprint(temp.ncattrs)
    #pprint(temp[0][0].tolist())
    #pprint(file.file_format)
    #print file.dimensions.values()
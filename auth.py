import re

def es_correo_valido(correo):
    patron = r'^[a-zA-Z0-9._%+-]+@(gmail|outlook|hotmail)\.com$'
    return re.match(patron, correo) is not None
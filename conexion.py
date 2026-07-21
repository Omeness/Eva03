from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

_cliente = None  # se crea una sola vez, la primera vez que se necesita


def _obtener_cliente():
    global _cliente
    if _cliente is None:
        _cliente = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    return _cliente


def ping_db():
    try:
        _obtener_cliente().admin.command("ping")
        return True
    except ServerSelectionTimeoutError:
        print("[Error] No se pudo conectar a MongoDB. Verifica que el servidor esté corriendo.")
        return False


def conexion(nombre_db):
    if not ping_db():
        raise Exception("[Error] Error de conexion. Verifica que el servidor esté corriendo.")
    return _obtener_cliente()[nombre_db]
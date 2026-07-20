from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def get_db(db_name):
    cliente = MongoClient("mongodb://localhost:27017/", ServerSelectionTimeoutMS=5000 )

    try:
        #accedemos a base de datos 'admin' y verificamos conexion
        cliente.admin.command('hello')
        print("Conexion exitosa")

        #retornamos la base de datos a trabajar
        return cliente[db_name]


    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"Error conexion: {e}")
        raise


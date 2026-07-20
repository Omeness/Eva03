from datetime import datetime
import os
from conexion import get_db

 
db = get_db("restaurante")
coleccion = db["menu"]


def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def continuar():
    print("\nVolviendo al menu...")
    input("Enter para continuar")

def seleccionar_categoria():
    categorias = {1: "Barra", 2: "Cocina"}

    while True:
        limpiar_pantalla()
        print("[1] Barra\n[2] Cocina")
        try:
            opcion = int(input("Selecciona una opcion: "))
            return categorias[opcion]
        except (ValueError, KeyError):
            print("\n[Error] Ingresa un numero de opcion valido.")
            input("Enter para continuar... ")

def leer_precio(mensaje="Precio producto: $"):
    precio = int(input(mensaje))
    if precio <= 0:
        raise ValueError("El precio debe ser un valor positivo")
    return precio


def leer_fecha(mensaje):
    """
    Pide una fecha en formato YYYY-MM-DD y la convierte a datetime.
    Vuelve a preguntar si el formato es inválido.
    """
    while True:
        texto = input(mensaje).strip()
        try:
            return datetime.strptime(texto, "%Y-%m-%d")
        except ValueError:
            print("[Error] Formato inválido. Usa AAAA-MM-DD (ej: 2026-07-25).")


def pedir_ingredientes():
    """
    Pide ingredientes en un loop hasta que el usuario decida no agregar más.
    Devuelve una lista de dicts {"nombre": str, "fecha_vencimiento": datetime}.
    """
    ingredientes = []
    print("\n-- Ingredientes (opcional) --")
    while True:
        limpiar_pantalla()
        agregar = input("¿Agregar un ingrediente? (s/n): ").strip().lower()
        if agregar != "s":
            break
 
        nombre_ing = input("  Nombre del ingrediente: ").strip().capitalize()
        if not nombre_ing:
            print("  [Error] El nombre no puede estar vacío.")
            continue
 
        fecha_venc = leer_fecha("  Fecha de vencimiento (AAAA-MM-DD): ")
        ingredientes.append({"nombre": nombre_ing, "fecha_vencimiento": fecha_venc})
 
    return ingredientes


def actualizar_fecha_vencimiento(nombre_plato, nombre_ingrediente, nueva_fecha):
    resultado = coleccion.update_one(
        {
            "nombre": nombre_plato,
            "ingredientes.nombre": nombre_ingrediente
        },
        {
            "$set": {"ingredientes.$.fecha_vencimiento": nueva_fecha}
        }
    )

    if resultado.matched_count == 0:
        raise ValueError(
            f"No se encontró el ingrediente '{nombre_ingrediente}' en el plato '{nombre_plato}'."
        )
    return resultado.modified_count > 0


def ingredientes_vencidos():
    """Platos que tienen al menos un ingrediente ya vencido."""
    ahora = datetime.now()
    return list(coleccion.find({"ingredientes.fecha_vencimiento": {"$lt": ahora}}))


def imprimir_platos_con_ingredientes(items):
    ROJO = "\033[91m"
    RESET = "\033[0m"
    ahora = datetime.now()
    for item in items:
        print(f"\n{item['nombre']} ({item['categoria']})")
        for ing in item.get("ingredientes", []):
            fecha = ing["fecha_vencimiento"]
            if fecha < ahora:
                print(f"{ROJO}  - {ing['nombre']} (vence: {fecha.strftime("%Y-%m-%d")}{RESET})")
            else:
                print(f"  - {ing['nombre']} (vence: {fecha.strftime("%Y-%m-%d")})")


def agregar_item(nombre, categoria, precio, ingredientes=None):
    """
    ingredientes: lista de dicts {"nombre": str, "fecha_vencimiento": datetime}
    """
    item = {
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "fecha_creacion": datetime.now(),
        "ingredientes": ingredientes if ingredientes else []
    }
    resultado = coleccion.insert_one(item)
    return coleccion.find_one({"_id": resultado.inserted_id})


def buscar_item(nombre_item):
    resultado = coleccion.find_one({"nombre": nombre_item})
    if not resultado:
        raise ValueError("El producto no esta en el menu.")
    return resultado


def actualizar_item(nombre_item, campo, valor):
    filtro = {"nombre": nombre_item}
    nuevo_valor = {"$set": {campo: valor}}
    resultado = coleccion.update_one(filtro, nuevo_valor)
    return resultado


def agregar_ingrediente(nombre_producto, nombre_ingrediente, fecha_vencimiento):
    resultado = coleccion.update_one(
        {"nombre": nombre_producto},
        {"$addToSet": {"ingredientes": {
            "nombre": nombre_ingrediente,
            "fecha_vencimiento": fecha_vencimiento
        }}}
    )
    if resultado.matched_count == 0:
        raise ValueError(f"No se encontró '{nombre_producto}' en el menú.")
    if resultado.modified_count == 0:
        raise ValueError("El ingrediente ya estaba ingresado.")


def platos_disponibles():
    """Platos donde NINGÚN ingrediente está vencido (disponibilidad derivada)."""
    ahora = datetime.now()
    return list(coleccion.find({
        "ingredientes": {"$not": {"$elemMatch": {"fecha_vencimiento": {"$lt": ahora}}}}
    }))



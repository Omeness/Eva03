from datetime import datetime
from conexion import conexion, ping_db
import os
import re


DATA_BASE = "restaurante"
COLECTION = "menu"

try:
    db = conexion(DATA_BASE)
    coleccion = db[COLECTION]
except Exception as e:
    print(e)

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
            input("Intenta de nuevo. Enter para continuar... ")


def leer_precio(mensaje="Precio producto: $"):
    """
    Pide ingresar el precio de un producto.
    Vuelve a preguntar si el valor es inválido.
    """
    while True:
        try:
            limpiar_pantalla()
            precio = int(input(mensaje))
            if precio <= 0:
                raise ValueError("[Error] El precio debe ser un valor positivo")
            return precio
        except ValueError as e:
            print("[Error] Valor invalido. El precio debe ser un numero entero.")
            input("\nIntenta de nuevo. Enter para continuar...")

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
    """Busca un documento por nombre dentro de la coleccion"""
    resultado = coleccion.find_one({"nombre": nombre_item})
    if not resultado:
        raise ValueError("El producto no esta en el menu.")
    return resultado


def actualizar_item(nombre_item, campo, valor):
    filtro = {"nombre": nombre_item}
    nuevo_valor = {"$set": {campo: valor}}
    resultado = coleccion.update_one(filtro, nuevo_valor)
    return resultado


def existe_ingrediente(nombre_producto, nombre_ingrediente):
    """Devuelve True si el producto ya tiene un ingrediente con ese nombre."""
    return coleccion.find_one({
        "nombre": nombre_producto,
        "ingredientes.nombre": nombre_ingrediente
    }) is not None


def agregar_ingrediente(nombre_producto, nombre_ingrediente, fecha_vencimiento):
    if existe_ingrediente(nombre_producto, nombre_ingrediente):
        raise ValueError(
            f"'{nombre_ingrediente}' ya existe en '{nombre_producto}'. "
            "Usa la opción 'Actualizar fecha vencimiento' en vez de agregar."
        )

    resultado = coleccion.update_one(
        {"nombre": nombre_producto},
        {"$push": {"ingredientes": {
            "nombre": nombre_ingrediente,
            "fecha_vencimiento": fecha_vencimiento
        }}}
    )
    if resultado.matched_count == 0:
        raise ValueError(f"No se encontró '{nombre_producto}' en el menú.")


def platos_disponibles():
    """Platos donde NINGÚN ingrediente está vencido (disponibilidad derivada)."""
    ahora = datetime.now()
    return list(coleccion.find({
        "ingredientes": {"$not": {"$elemMatch": {"fecha_vencimiento": {"$lt": ahora}}}}
    }))


def sugerir_platos(patron, limite=3):
    """Busca platos cuyo nombre contenga 'patron' (case-insensitive, regex)."""
    regex = re.compile(re.escape(patron), re.IGNORECASE)
    return list(coleccion.find({"nombre": regex}).limit(limite))


def buscar_plato_interactivo(mensaje="Ingresa el nombre de la preparacion: "):
    """
    Pide el nombre de un plato. Si no hay coincidencia exacta, busca por
    regex y muestra hasta 3 sugerencias para que el usuario elija.
    Devuelve el documento del plato encontrado, o None si no hay match
    o el usuario cancela.
    """
    nombre = input(mensaje).strip().capitalize()

    try:
        return buscar_item(nombre)
    except ValueError:
        pass  # no hubo match exacto, probamos con sugerencias

    sugerencias = sugerir_platos(nombre)
    if not sugerencias:
        print(f"No se encontró '{nombre}' ni coincidencias similares en el menú.")
        return None

    print(f"No se encontró '{nombre}' exactamente. ¿Quisiste decir alguno de estos?")
    for i, s in enumerate(sugerencias, start=1):
        print(f"  [{i}] {s['nombre']} ({s['categoria']}) - ${s['precio']}")
    print("  [0] Cancelar")

    try:
        opcion = int(input("Selecciona una opción: "))
    except ValueError:
        print("Opción inválida.")
        return None

    if opcion < 1 or opcion > len(sugerencias):
        return None
    limpiar_pantalla()
    seleccion = sugerencias[opcion - 1]
    print(f"Seleccionaste: {seleccion.get('nombre')}")
    return seleccion


def sugerir_ingredientes(ingredientes_lista, patron, limite=3):
    """Filtra localmente por coincidencia parcial."""
    regex = re.compile(re.escape(patron), re.IGNORECASE)
    return [ing for ing in ingredientes_lista if regex.search(ing["nombre"])][:limite]


def seleccionar_ingrediente_interactivo(plato, mensaje="Nombre del ingrediente: "):
    """
    Pide el nombre de un ingrediente que pertenezca a 'plato'. Si no hay
    coincidencia exacta, sugiere hasta 3 por similitud. Devuelve
    el nombre EXACTO del ingrediente ya validado, o None si no existe o
    el usuario cancela.
    """
    ingredientes = plato.get("ingredientes", [])
    if not ingredientes:
        print(f"'{plato['nombre']}' no tiene ingredientes registrados.")
        return None

    nombre = input(mensaje).strip().capitalize()

    for ing in ingredientes:
        if ing["nombre"] == nombre:
            return nombre

    sugerencias = sugerir_ingredientes(ingredientes, nombre)
    if not sugerencias:
        print(f"'{nombre}' no es un ingrediente de '{plato['nombre']}'.")
        return None

    print(f"'{nombre}' no coincide exactamente. ¿Quisiste decir alguno de estos?")
    for i, s in enumerate(sugerencias, start=1):
        fecha = s["fecha_vencimiento"].strftime("%Y-%m-%d")
        print(f"  [{i}] {s['nombre']} (vence: {fecha})")
    print("  [0] Cancelar")

    try:
        opcion = int(input("Selecciona una opción: "))
    except ValueError:
        print("Opción inválida.")
        return None

    if opcion < 1 or opcion > len(sugerencias):
        return None

    return sugerencias[opcion - 1]["nombre"]
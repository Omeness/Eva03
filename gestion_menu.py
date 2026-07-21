from validaciones import *

def menu_menu():
    print("""
=== Gestion Menu ===

[1] Agregar producto.
[2] Eliminar producto.
[3] Actualizar producto.
[4] Buscar producto.
[5] Ver todos los productos.
[6] Ver productos disponibles.
[7] Ver ingrdientes por vencer.
[8] Salir.
    """)


def agregar_producto():
    print("=== Agregar producto ===\n")
 
    try:
        nombre = input("Nombre producto: ").strip().capitalize()
        if not nombre:
            raise ValueError("El nombre no puede estar vacio")
        
        categoria = seleccionar_categoria()
        limpiar_pantalla()
        precio = leer_precio()
        ingredientes = pedir_ingredientes()
 
        item = agregar_item(nombre, categoria, precio, ingredientes)
        print(f"\nSe agrego '{nombre}' al menu. ({len(ingredientes)} ingrediente(s))")
 
    except ValueError as e:
        print("\n[Error]:",e)
        print("** No se agregaron productos al menu **")


def eliminar_producto():
    print("=== Eliminar producto ===\n")

    item = buscar_plato_interactivo()
    if item is None:
        return

    nombre = item["nombre"]
    confirmacion = input(
        f"Seguro que quieres eliminar '{nombre}'? Escribe 'eliminar' para confirmar: ")

    if confirmacion == "eliminar":
        coleccion.delete_one({"nombre": nombre})
        print(f"Se elimino '{nombre}' del menu.")
    else:
        print("Eliminacion cancelada.")


def actualizar_producto():
    print("=== Actualizar Item ===\n")

    item = buscar_plato_interactivo()
    if item is None:
        return

    nombre = item.get("nombre")

    print("Que deseas actualizar?")
    print("[1] Nombre\n[2] Categoria\n[3] Precio")
    print("[4] Agregar ingrediente\n[5] Actualizar fecha vencimiento")

    try:
        campo = int(input("Selecciona una opcion: "))

        if campo == 1:
            valor = input("Ingresa el nuevo nombre: ").strip().capitalize()
            actualizar_item(nombre, "nombre", valor)
            print(f"Nombre actualizado de '{nombre}' a '{valor}'")

        elif campo == 2:
            valor = seleccionar_categoria()
            categoria_anterior = item.get("categoria")
            actualizar_item(nombre, "categoria", valor)
            print(f"Categoria actualizada de '{categoria_anterior}' a '{valor}'")

        elif campo == 3:
            valor = leer_precio("Ingresa el nuevo precio: $")
            precio_anterior = item.get("precio")
            actualizar_item(nombre, "precio", valor)
            print(f"Precio actualizado de ${precio_anterior} a ${valor}")
        
        elif campo == 4:
            limpiar_pantalla()
            nombre_ingrediente = input("Nombre del nuevo ingrediente: ").strip().capitalize()
            if not nombre_ingrediente:
                raise ValueError("El nombre del ingrediente no puede estar vacio")
 
            fecha_venc = leer_fecha("Fecha de vencimiento (AAAA-MM-DD): ")
            agregar_ingrediente(nombre, nombre_ingrediente, fecha_venc)
            print(f"Se agrego '{nombre_ingrediente}' (vence: {fecha_venc.strftime('%Y-%m-%d')}) a '{nombre}'")

        elif campo == 5:
            limpiar_pantalla()
            plato = item

            ingredientes = plato.get("ingredientes", [])
            if not ingredientes:
                print(f"'{nombre}' no tiene ingredientes registrados.")
                return

            print(f"\nIngredientes de '{nombre}':")
            for ing in ingredientes:
                fecha_actual = ing["fecha_vencimiento"].strftime("%Y-%m-%d")
                print(f"  - {ing['nombre']} (vence: {fecha_actual})")

            nombre_ingrediente = seleccionar_ingrediente_interactivo(
                plato, "\nNombre del ingrediente a actualizar: "
            )
            if nombre_ingrediente is None:
                return

            nueva_fecha = leer_fecha("Nueva fecha de vencimiento (AAAA-MM-DD): ")
            actualizar_fecha_vencimiento(nombre, nombre_ingrediente, nueva_fecha)
            print(f"\nFecha de '{nombre_ingrediente}' actualizada a {nueva_fecha.strftime('%Y-%m-%d')}.")


        else:
            limpiar_pantalla()
            raise ValueError("Opcion fuera de rango.")

    except ValueError as e:
        limpiar_pantalla()
        print("\n[Error]:", e)


def buscar_producto():
    ROJO = "\033[91m"
    RESET = "\033[0m"
    ahora = datetime.now()
    print("=== Buscar Item ===\n")

    item = buscar_plato_interactivo()
    if item is None:
        return
    limpiar_pantalla()

    print("-" * 10, "Producto encontrado", "-" * 10)
    print(f"Producto: {item.get('nombre')}")
    print(f"Categoria: {item.get('categoria')}")
    print(f"Precio: ${item.get('precio')}")
 
    ingredientes = item.get("ingredientes", [])
    if ingredientes:
        print("Ingredientes:")
        for ing in ingredientes:
            fecha = ing["fecha_vencimiento"]
            if fecha < ahora:
                print(f"{ROJO}  - {ing['nombre']} (vence: {fecha.strftime("%Y-%m-%d")}{RESET})")
            else:
                print(f"  - {ing['nombre']} (vence: {fecha.strftime("%Y-%m-%d")})")
    else:
        print("Ingredientes: (sin registrar)")
    print("-" * 41, "\n")


def ver_items():
    items = list(coleccion.find({}))
    print("=== Catalogo ===\n")
    if not items:
        print("El menú está vacío.")
        return
 
    for item in items:
        print(f"- {item['nombre']:<25} | {item['categoria']:<8} | ${item['precio']}")


def ver_disponibles():
    print("=== Platos disponibles ===\n")
 
    disponibles = platos_disponibles()
    if not disponibles:
        print("No hay platos disponibles en este momento.")
        return
    
    imprimir_platos_con_ingredientes(disponibles)


def alerta_ingredientes():
    print("=== Alertas de vencimiento ===\n")
 
    vencidos = ingredientes_vencidos()
    print(f"-- Ingredientes YA VENCIDOS. ({len(vencidos)} plato(s) afectados) --")
    if vencidos:
        imprimir_platos_con_ingredientes(vencidos)
    else:
        print("Ninguno.")
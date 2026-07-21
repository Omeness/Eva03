from validaciones import limpiar_pantalla, continuar
from conexion import conexion, ping_db
from gestion_menu import (
    menu_menu,
    agregar_producto,
    eliminar_producto,
    actualizar_producto,
    buscar_producto,
    ver_items,
    ver_disponibles,
    alerta_ingredientes,
)


if ping_db():
    while True:
        limpiar_pantalla()
        menu_menu()
        try:
            while True:
                opcion = int(input("Selecciona el numero de opcion: "))
                if opcion < 1 or opcion > 8:
                    limpiar_pantalla()
                    print("\n[Error] Ingresa un numero de opcion valido.")
                    input(f"Valor ingresado: {opcion}.\nEnter para continuar... ")
                    menu_menu()
                else:
                    break
            
            if opcion == 1:
                limpiar_pantalla()
                agregar_producto()
                continuar()

            if opcion == 2:
                limpiar_pantalla()
                eliminar_producto()                
                continuar()

            if opcion == 3:
                limpiar_pantalla()
                actualizar_producto()
                continuar()                 

            if opcion == 4:
                limpiar_pantalla()
                buscar_producto()
                continuar()

            if opcion == 5:
                limpiar_pantalla()
                ver_items()
                continuar()

            if opcion == 6:
                limpiar_pantalla()
                ver_disponibles()
                continuar()

            if opcion == 7:
                limpiar_pantalla()
                alerta_ingredientes()
                continuar()

            if opcion == 8:
                limpiar_pantalla()
                print("-----------------------")
                print("Saliendo del sistema...")
                break
            
        except Exception as e:
            limpiar_pantalla()
            print("[Error] Valor invalido:",e)
            continuar()
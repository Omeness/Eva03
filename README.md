# Gestión de Menú - App de Consola (TUI)

Aplicación de consola (TUI) para la gestión de platos de un restaurante, desarrollada en Python con MongoDB como base de datos.

## Alcance

La aplicación permite el ingreso, modificación y eliminación de platos en una base de datos local.

También permite agregar ingredientes, junto con su fecha de vencimiento, a los distintos platos del menú.

Adicionalmente, permite:

- Visualizar todos los productos registrados en el sistema.
- Visualizar los productos disponibles (aquellos que no tienen ingredientes vencidos).
- Visualizar los productos con ingredientes vencidos.

## Detalles por implementar

- Uso de expresiones regulares (regex) para mejorar el filtrado de productos y/o ingredientes.
- En el apartado de actualización de fecha de vencimiento de ingredientes: actualmente, si el ingrediente ingresado no existe en la preparación seleccionada, el sistema igualmente permite ingresar una fecha de vencimiento. Esto no debería ocurrir; el sistema debería verificar primero si el ingrediente existe en la preparación antes de solicitar la nueva fecha.

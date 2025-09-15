import pandas as pd
from docxtpl import DocxTemplate

def UnSoloPrecio(tabla_data, precio_total):
    while True:
        print(f"\n--- Nuevo Item ---")
        cant = input("Cantidad: ").strip()
        descripcion = input("Descripción: ").strip()
        precio_unit_str = input("Precio unitario: ").strip()

        if precio_unit_str:  # si se ingresó algo en precio
            precio_unit = float(precio_unit_str)
            precio_total += precio_unit

            tabla_data.append({
                'cant': cant,
                'descripcion': descripcion,
                'preciounit': f"${precio_unit:,.2f}",
                'preciototal': f"${precio_total:,.2f}"
            })
        else:
            tabla_data.append({
                'cant': cant,
                'descripcion': descripcion,
                'preciounit': "",
                'preciototal': ""
            })

        continuar = input("¿Desea ingresar otro producto/servicio? (S/N): ").strip().upper()
        if continuar != "S":
            break

    return tabla_data, precio_total
def PrecioSeparado(tabla_data, precio_total):
    while True:
        print(f"\n--- Nuevo Item ---")
        cant = input("Cantidad: ").strip()
        descripcion = input("Descripción: ").strip()
        precio_unit_str = input("Precio unitario: ").strip()

        if precio_unit_str:
            precio_unit = float(precio_unit_str)
            precio_unit_total = precio_unit
            precio_total += precio_unit_total

            tabla_data.append({
                'cant': cant,
                'descripcion': descripcion,
                'preciounit': f"${precio_unit:,.2f}",
                'preciototal': f"${precio_unit_total:,.2f}"
            })
        else:
            tabla_data.append({
                'cant': cant,
                'descripcion': descripcion,
                'preciounit': "",
                'preciototal': ""
            })

        continuar = input("¿Desea ingresar otro producto/servicio? (S/N): ").strip().upper()
        if continuar != "S":
            break

    return tabla_data, precio_total

# ==========================
# Pedir datos generales
# ==========================
fecha = input("Ingrese la fecha (dd/mm/aaaa): ")
cotizacion = input("Ingrese el número de cotización: ")
cliente = input("Ingrese el nombre del cliente: ")
direccion = input("Ingrese la dirección: ")
correo = input("Ingrese el correo: ")
telefono = input("Ingrese el teléfono: ")
terminos = input("Ingrese los términos: ")

# ==========================
# Pedir datos de la tabla con while
# ==========================
tabla_data = []
precio_total = 0

decision = input('¿La lista tendrá precios separados para cada cosa de la lista? (S/N): ').strip().upper()
if decision == 'S':
    tabla_data, precio_total = PrecioSeparado(tabla_data, precio_total)
else:
    tabla_data, precio_total = UnSoloPrecio(tabla_data, precio_total)

tabla_df = pd.DataFrame(tabla_data)

subtotal = precio_total
impuesto = input('¿Deseas agregar IVA? (S/N): ').strip().upper()
if impuesto != 'N':
    iva = precio_total * .16
else:
    iva = 0

total = iva + subtotal

# ==========================
# Generar documento
# ==========================
doc = DocxTemplate('Plantilla_nueva.docx')
ultimos3 = cotizacion[-3:]
ultimos3 = str(int(ultimos3))

context = {
    'fecha': fecha,
    'cotizacion': cotizacion,
    'cliente': cliente,
    'direccion': direccion,
    'correo': correo,
    'telefono': telefono,
    'tabla': tabla_df.to_dict(orient='records'),
    'terminos': terminos,
    'subtotal': f"${subtotal:,.2f}",
    'iva': f"${iva:,.2f}",
    'total': f"${total:,.2f}"
}

doc.render(context)
doc.save(f"Multiservicios{ultimos3}.docx")
print(f"\n✅ Documento generado: Multiservicios{ultimos3}.docx")

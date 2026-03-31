from flask import Flask, request, send_file, send_from_directory
from docxtpl import DocxTemplate
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
TEMP_DIR = os.path.join(BASE_DIR, "temp_download")
os.makedirs(TEMP_DIR, exist_ok=True)


# =========================
# VISTAS
# =========================
@app.route('/')
def menu():
    return send_from_directory('.', 'menu.html')


@app.route('/proforma')
def proforma():
    return send_from_directory('.', 'index.html')


@app.route('/orden-trabajo')
def orden_trabajo():
    return send_from_directory('.', 'orden_trabajo.html')


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)


# =========================
# GENERAR PROFORMA
# =========================
@app.route('/generar', methods=['POST'])
def generar_cotizacion():
    try:
        data = request.json

        fecha = data.get('fecha', '')
        cotizacion = data.get('cotizacion', '000')
        cliente = data.get('cliente', '')
        direccion = data.get('direccion', '')
        correo = data.get('correo', '')
        telefono = data.get('telefono', '')
        terminos = data.get('terminos', '')
        productos = data.get('productos', [])
        aplicar_iva = data.get('iva', False)

        tabla_data = []
        precio_total = 0

        for item in productos:
            cant = item.get('cantidad', '')
            desc = item.get('descripcion', '')
            precio_unit_str = item.get('precio', '')

            if precio_unit_str:
                precio_unit = float(precio_unit_str)
                precio_total += precio_unit
                tabla_data.append({
                    'cant': cant,
                    'descripcion': desc,
                    'preciounit': f"${precio_unit:,.2f}",
                    'preciototal': f"${precio_unit:,.2f}"
                })
            else:
                tabla_data.append({
                    'cant': cant,
                    'descripcion': desc,
                    'preciounit': "",
                    'preciototal': ""
                })

        subtotal = precio_total
        iva = subtotal * 0.16 if aplicar_iva else 0
        total = subtotal + iva

        ultimos3 = cotizacion[-3:]
        ultimos3 = str(int(ultimos3)) if ultimos3.isdigit() else '000'
        base_name = f"Multiservicios{ultimos3}"

        plantilla_path = os.path.join(BASE_DIR, "Plantilla_nueva.docx")
        doc = DocxTemplate(plantilla_path)

        context = {
            'fecha': fecha,
            'cotizacion': cotizacion,
            'cliente': cliente,
            'direccion': direccion,
            'correo': correo,
            'telefono': telefono,
            'tabla': tabla_data,
            'terminos': terminos,
            'subtotal': f"${subtotal:,.2f}",
            'iva': f"${iva:,.2f}",
            'total': f"${total:,.2f}"
        }

        doc.render(context)

        word_path = os.path.join(TEMP_DIR, f"{base_name}.docx")
        doc.save(word_path)

        return send_file(word_path, as_attachment=True)

    except Exception as e:
        return f"Error en proforma: {e}", 500


# =========================
# GENERAR ORDEN DE TRABAJO
# =========================
@app.route('/generar-ot', methods=['POST'])
def generar_orden_trabajo():
    try:
        data = request.json

        fecha = data.get('fecha', '')
        folio = data.get('folio', '')
        cliente = data.get('cliente', '')
        direccion = data.get('direccion', '')
        correo = data.get('correo', '')
        telefono = data.get('telefono', '')
        diagnostico = data.get('diagnostico', '')
        terminos = data.get('terminos', '')

        tipo_servicio = data.get('tipoServicio', '')
        otro_servicio = data.get('otroServicio', '')
        areas = data.get('areas', [])
        forma_pago = data.get('formaPago', '')

        conceptos = data.get('conceptos', [])
        subtotal = float(data.get('subtotal', 0) or 0)
        iva = float(data.get('iva', 0) or 0)
        total = float(data.get('total', 0) or 0)

        tabla_items = []
        for item in conceptos:
            numero = item.get('numero', '')
            descripcion = item.get('descripcion', '')
            precio_unitario = float(item.get('precio_unitario', 0) or 0)
            total_item = float(item.get('total', 0) or 0)

            tabla_items.append({
                'cantidad': numero,
                'descripcion': descripcion,
                'precio_uni': f"${precio_unitario:,.2f}" if precio_unitario else "",
                'total': f"${total_item:,.2f}" if total_item else ""
            })

        context = {
            'Fecha': fecha,
            'Folio': folio,
            'Cliente': cliente,
            'Direccion': direccion,
            'Correo': correo,
            'Telefono': telefono,
            'Diagnostico': diagnostico,
            'Terminos': terminos,

            'MP': 'X' if tipo_servicio == 'Mantenimiento Preventivo' else '',
            'MC': 'X' if tipo_servicio == 'Mantenimiento Correctivo' else '',
            'R': 'X' if tipo_servicio == 'Reparación' else '',
            'I': 'X' if tipo_servicio == 'Instalación' else '',
            'O': 'X' if tipo_servicio == 'Otro' else '',
            'OtroTexto': otro_servicio,

            'IM': 'X' if 'Impermeabilización' in areas else '',
            'P': 'X' if 'Plomería' in areas else '',
            'E': 'X' if 'Electricidad' in areas else '',
            'PI': 'X' if 'Pintura' in areas else '',
            'A': 'X' if 'Albañilería' in areas else '',
            'S': 'X' if 'Soldadura' in areas else '',

            'EF': 'X' if forma_pago == 'Efectivo' else '',
            'TR': 'X' if forma_pago == 'Transferencia' else '',

            'items': tabla_items,

            'subtotal': f"{subtotal:,.2f}",
            'IVA': f"{iva:,.2f}",
            'total': f"{total:,.2f}"
        }

        plantilla_path = os.path.join(BASE_DIR, "PLANTILLA_ORDEN_DE_TRABAJO_PY.docx")
        doc = DocxTemplate(plantilla_path)
        doc.render(context)

        nombre_archivo = f"OrdenTrabajo_{folio if folio else 'prueba'}.docx"
        word_path = os.path.join(TEMP_DIR, nombre_archivo)
        doc.save(word_path)

        return send_file(word_path, as_attachment=True)

    except Exception as e:
        return f"Error en orden de trabajo: {e}", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
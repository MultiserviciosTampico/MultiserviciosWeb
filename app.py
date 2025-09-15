from flask import Flask, request, send_file, send_from_directory
from docxtpl import DocxTemplate
import os

app = Flask(__name__)

# Carpeta de descarga temporal dentro del proyecto
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_download")
os.makedirs(TEMP_DIR, exist_ok=True)

# -----------------------------
# Servir index.html y archivos estáticos
# -----------------------------
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# -----------------------------
# Endpoint para generar la cotización
# -----------------------------
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

        # -----------------------------
        # Construir tabla de productos
        # -----------------------------
        tabla_data = []
        precio_total = 0
        for item in productos:
            cant = item['cantidad']
            desc = item['descripcion']
            precio_unit_str = item['precio']

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

        # -----------------------------
        # Generar Word en carpeta temporal
        # -----------------------------
        ultimos3 = cotizacion[-3:]
        ultimos3 = str(int(ultimos3)) if ultimos3.isdigit() else '000'
        base_name = f"Multiservicios{ultimos3}"

        plantilla_path = os.path.join(os.path.dirname(__file__), "Plantilla_nueva.docx")
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

        # Enviar Word al cliente
        return send_file(word_path, as_attachment=True)

    except Exception as e:
        return f"Error: {e}", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)

from flask import Flask, request, send_file, send_from_directory
from docxtpl import DocxTemplate
from fpdf import FPDF
import os
import zipfile

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
# Función para generar PDF con FPDF
# -----------------------------
def generar_pdf(pdf_path, datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, f"Cotización: {datos['cotizacion']}", ln=True)
    pdf.cell(0, 10, f"Fecha: {datos['fecha']}", ln=True)
    pdf.cell(0, 10, f"Cliente: {datos['cliente']}", ln=True)
    pdf.cell(0, 10, f"Dirección: {datos['direccion']}", ln=True)
    pdf.cell(0, 10, f"Correo: {datos['correo']}", ln=True)
    pdf.cell(0, 10, f"Teléfono: {datos['telefono']}", ln=True)
    pdf.cell(0, 10, "------------------------------------------", ln=True)

    # Tabla de productos
    pdf.cell(40, 10, "Cantidad", border=1)
    pdf.cell(80, 10, "Descripción", border=1)
    pdf.cell(35, 10, "Precio Unitario", border=1)
    pdf.cell(35, 10, "Precio Total", border=1)
    pdf.ln()

    for item in datos['tabla']:
        pdf.cell(40, 10, str(item['cant']), border=1)
        pdf.cell(80, 10, item['descripcion'], border=1)
        pdf.cell(35, 10, item['preciounit'], border=1)
        pdf.cell(35, 10, item['preciototal'], border=1)
        pdf.ln()

    pdf.cell(0, 10, "------------------------------------------", ln=True)
    pdf.cell(0, 10, f"Subtotal: {datos['subtotal']}", ln=True)
    pdf.cell(0, 10, f"IVA: {datos['iva']}", ln=True)
    pdf.cell(0, 10, f"Total: {datos['total']}", ln=True)
    pdf.cell(0, 10, f"Términos: {datos['terminos']}", ln=True)

    pdf.output(pdf_path)


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
        # Generar Word + PDF + ZIP en carpeta temporal
        # -----------------------------
        ultimos3 = cotizacion[-3:]
        ultimos3 = str(int(ultimos3)) if ultimos3.isdigit() else '000'
        base_name = f"Multiservicios{ultimos3}"

        # Generar Word
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

        # Generar PDF con FPDF
        pdf_path = os.path.join(TEMP_DIR, f"{base_name}.pdf")
        generar_pdf(pdf_path, context)

        # Crear ZIP con ambos archivos
        zip_path = os.path.join(TEMP_DIR, f"{base_name}.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(word_path, arcname=f"{base_name}.docx")
            zipf.write(pdf_path, arcname=f"{base_name}.pdf")

        # Enviar ZIP al cliente
        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        return f"Error: {e}", 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)


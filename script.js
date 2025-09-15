document.addEventListener('DOMContentLoaded', () => {
  const addBtn = document.querySelector('.add-btn');
  const productsContainer = document.querySelector('.products');
  const ivaCheckbox = document.querySelector('#toggle-iva');

  // Función para actualizar totales
  function actualizarTotales() {
    let subtotal = 0;
    document.querySelectorAll('.product-row').forEach(row => {
      const inputs = row.querySelectorAll('input');
      const precio = parseFloat(row.querySelector('input[placeholder="Precio"]').value) || 0;
      subtotal += precio;
    });

    const aplicarIva = document.querySelector('#toggle-iva').checked;
    const ivaTotal = aplicarIva ? subtotal * 0.16 : 0;
    const total = subtotal + ivaTotal;

    document.querySelector('.summary div:nth-child(1) span:last-child').textContent = `$${subtotal.toFixed(2)}`;
    document.querySelector('.summary div:nth-child(2) span:last-child').textContent = `$${ivaTotal.toFixed(2)}`;
    document.querySelector('.summary .total span:last-child').textContent = `$${total.toFixed(2)}`;
  }

  // -----------------------------
  // Añadir listener a inputs de precio existentes
  // -----------------------------
  document.querySelectorAll('.product-row input[placeholder="Precio"]').forEach(input => {
    input.addEventListener('input', actualizarTotales);
  });

  // BOTÓN AGREGAR PRODUCTO
  addBtn.addEventListener('click', () => {
    const newRow = document.createElement('div');
    newRow.classList.add('product-row');

    const inputCant = document.createElement('input');
    inputCant.type = 'text';
    inputCant.placeholder = 'Cant.';

    const inputDesc = document.createElement('input');
    inputDesc.type = 'text';
    inputDesc.placeholder = 'Descripción';

    const inputPrecio = document.createElement('input');
    inputPrecio.type = 'text';
    inputPrecio.placeholder = 'Precio';
    // Escuchar cambios para actualizar totales
    inputPrecio.addEventListener('input', actualizarTotales);

    // Botón de eliminar producto
    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.textContent = '🗑️';
    deleteBtn.classList.add('delete-btn');
    deleteBtn.addEventListener('click', () => {
    newRow.remove();
    actualizarTotales();
  });

    newRow.appendChild(inputCant);
    newRow.appendChild(inputDesc);
    newRow.appendChild(inputPrecio);
    newRow.appendChild(deleteBtn);

    productsContainer.appendChild(newRow);
  });

  // Checkbox IVA actualiza totales al cambiar
  ivaCheckbox.addEventListener('change', actualizarTotales);

  // Inicializamos los totales al cargar la página
  actualizarTotales();

  // BOTÓN GENERAR COTIZACIÓN
  const generateBtn = document.querySelector('.generate-btn');
  generateBtn.addEventListener('click', async () => {
    const fecha = document.querySelector('input[placeholder="Fecha"]').value;
    const cotizacion = document.querySelector('input[placeholder="No. Cotización"]').value;
    const cliente = document.querySelector('input[placeholder="Nombre del Cliente"]').value;
    const direccion = document.querySelector('input[placeholder="Dirección"]').value;
    const correo = document.querySelector('input[placeholder="Correo"]').value;
    const telefono = document.querySelector('input[placeholder="Teléfono"]').value;
    const terminos = document.querySelector('textarea[placeholder="Términos y Condiciones"]').value;

    // Recalcular antes de enviar
    actualizarTotales();

    // Obtener productos
    const productos = [];
    document.querySelectorAll('.product-row').forEach(row => {
      const inputs = row.querySelectorAll('input');
      productos.push({
        cantidad: inputs[0].value,
        descripcion: inputs[1].value,
        precio: parseFloat(inputs[2].value) || 0
      });
    });

    // Estado del IVA
    const aplicarIva = ivaCheckbox.checked;

    // Enviar datos al servidor
    const response = await fetch('/generar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fecha, cotizacion, cliente, direccion, correo, telefono,
        terminos, productos, iva: aplicarIva
      })
    });

    // Recibir archivo
const blob = await response.blob();

// Sacar últimos 3 dígitos de la cotización
let ultimos3 = cotizacion.slice(-3);
if (!/^\d+$/.test(ultimos3)) {
  ultimos3 = "000"; // fallback si no son números
}

// Crear el enlace de descarga
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;

// Usar nombre dinámico para el ZIP
a.download = `Multiservicios${ultimos3}.zip`;

document.body.appendChild(a);
a.click();
a.remove();
  });
});

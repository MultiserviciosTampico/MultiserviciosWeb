document.addEventListener('DOMContentLoaded', () => {
  const addBtn = document.querySelector('.add-btn');
  const productsContainer = document.querySelector('.products');
  const ivaCheckbox = document.querySelector('#toggle-iva');
  const generateBtn = document.querySelector('.generate-btn');
  const otroServicioInput = document.querySelector('#otro-servicio');
  const tipoServicioRadios = document.querySelectorAll('input[name="tipo-servicio"]');

  // =============================
  // CONFIGURAR INPUT "OTRO SERVICIO"
  // =============================
  otroServicioInput.disabled = true;

  function actualizarEstadoOtroServicio() {
    const radioOtro = Array.from(tipoServicioRadios).find(radio => {
      return radio.parentElement.textContent.trim().toLowerCase() === 'otro';
    });

    if (radioOtro && radioOtro.checked) {
      otroServicioInput.disabled = false;
    } else {
      otroServicioInput.disabled = true;
      otroServicioInput.value = '';
    }
  }

  tipoServicioRadios.forEach(radio => {
    radio.addEventListener('change', actualizarEstadoOtroServicio);
  });

  // =============================
  // CREAR BOTÓN ELIMINAR EN FILA INICIAL SI NO EXISTE
  // =============================
  function asegurarBotonEliminar(row) {
    let deleteBtn = row.querySelector('.delete-btn');

    if (!deleteBtn) {
      deleteBtn = document.createElement('button');
      deleteBtn.type = 'button';
      deleteBtn.textContent = '🗑️';
      deleteBtn.classList.add('delete-btn');
      row.appendChild(deleteBtn);
    }

    deleteBtn.addEventListener('click', () => {
      const rows = document.querySelectorAll('.product-row');
      if (rows.length > 1) {
        row.remove();
        actualizarTotales();
      } else {
        // Si solo queda una fila, mejor vaciarla
        const inputs = row.querySelectorAll('input');
        inputs.forEach(input => {
          if (input.type !== 'button') input.value = '';
        });
        actualizarTotales();
      }
    });
  }

  // =============================
  // CALCULAR TOTAL DE UNA FILA
  // =============================
  function actualizarFila(row) {
    const inputs = row.querySelectorAll('input');
    const noInput = inputs[0];
    const descripcionInput = inputs[1];
    const precioInput = inputs[2];
    const totalInput = inputs[3];

    const precio = parseFloat(precioInput.value) || 0;

    totalInput.value = `$${precio.toFixed(2)}`;
  }

  // =============================
  // ACTUALIZAR TOTALES GENERALES
  // =============================
  function actualizarTotales() {
    let subtotal = 0;

    document.querySelectorAll('.product-row').forEach(row => {
      const inputs = row.querySelectorAll('input');
      const precio = parseFloat(inputs[2].value) || 0;

      actualizarFila(row);
      subtotal += precio;
    });

    const aplicarIva = ivaCheckbox.checked;
    const ivaTotal = aplicarIva ? subtotal * 0.16 : 0;
    const otros = 0;
    const total = subtotal + ivaTotal + otros;

    document.querySelector('.summary div:nth-child(1) span:last-child').textContent = `$${subtotal.toFixed(2)}`;
    document.querySelector('.summary div:nth-child(2) span:last-child').textContent = `$${ivaTotal.toFixed(2)}`;
    document.querySelector('.summary div:nth-child(3) span:last-child').textContent = `$${otros.toFixed(2)}`;
    document.querySelector('.summary .total span:last-child').textContent = `$${total.toFixed(2)}`;
  }

  // =============================
  // ASIGNAR EVENTOS A UNA FILA
  // =============================
  function asignarEventosFila(row) {
    const inputs = row.querySelectorAll('input');
    const precioInput = inputs[2];

    precioInput.addEventListener('input', actualizarTotales);

    asegurarBotonEliminar(row);
  }

  // =============================
  // FILA INICIAL
  // =============================
  document.querySelectorAll('.product-row').forEach(row => {
    asignarEventosFila(row);
  });

  // =============================
  // AGREGAR NUEVO CONCEPTO
  // =============================
  addBtn.addEventListener('click', () => {
    const newRow = document.createElement('div');
    newRow.classList.add('product-row');

    const inputNo = document.createElement('input');
    inputNo.type = 'text';
    inputNo.placeholder = 'No.';

    const inputDesc = document.createElement('input');
    inputDesc.type = 'text';
    inputDesc.placeholder = 'Descripción';

    const inputPrecio = document.createElement('input');
    inputPrecio.type = 'text';
    inputPrecio.placeholder = 'P. Unit.';

    const inputTotal = document.createElement('input');
    inputTotal.type = 'text';
    inputTotal.placeholder = 'Total';
    inputTotal.readOnly = true;

    newRow.appendChild(inputNo);
    newRow.appendChild(inputDesc);
    newRow.appendChild(inputPrecio);
    newRow.appendChild(inputTotal);

    productsContainer.appendChild(newRow);

    asignarEventosFila(newRow);
    actualizarTotales();
  });

  // =============================
  // IVA
  // =============================
  ivaCheckbox.addEventListener('change', actualizarTotales);

  // =============================
  // GENERAR ORDEN DE TRABAJO
  // =============================
  generateBtn.addEventListener('click', async () => {
    const fecha = document.querySelector('#fecha').value;
    const folioNumero = document.querySelector('#folio').value.trim();
    const folioCompleto = `MST-${folioNumero || '000'}`;

    const cliente = document.querySelector('#cliente').value;
    const direccion = document.querySelector('#direccion').value;
    const correo = document.querySelector('#correo').value;
    const telefono = document.querySelector('#telefono').value;
    const diagnostico = document.querySelector('#diagnostico').value;

    const terminos = document.querySelector('textarea[placeholder="Escribe aquí los términos y condiciones"]').value;

    // Tipo de servicio seleccionado
    let tipoServicio = '';
    tipoServicioRadios.forEach(radio => {
      if (radio.checked) {
        tipoServicio = radio.parentElement.textContent.trim();
      }
    });

    const otroServicio = otroServicioInput.value.trim();

    // Áreas seleccionadas
    const areasSeleccionadas = [];
    document.querySelectorAll('input[name="area"]:checked').forEach(checkbox => {
      areasSeleccionadas.push(checkbox.parentElement.textContent.trim());
    });

    // Conceptos
    const conceptos = [];
    document.querySelectorAll('.product-row').forEach(row => {
      const inputs = row.querySelectorAll('input');
      conceptos.push({
        numero: inputs[0].value,
        descripcion: inputs[1].value,
        precio_unitario: parseFloat(inputs[2].value) || 0,
        total: parseFloat(inputs[2].value) || 0
      });
    });

    // Forma de pago
    let formaPago = '';
    document.querySelectorAll('input[name="pago"]').forEach(radio => {
      if (radio.checked) {
        formaPago = radio.parentElement.textContent.trim();
      }
    });

    // Totales
    let subtotal = 0;
    conceptos.forEach(item => {
      subtotal += item.total;
    });

    const aplicarIva = ivaCheckbox.checked;
    const iva = aplicarIva ? subtotal * 0.16 : 0;
    const total = subtotal + iva;

    try {
      const response = await fetch('/generar-ot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fecha,
          folio: folioCompleto,
          cliente,
          direccion,
          correo,
          telefono,
          diagnostico,
          tipoServicio,
          otroServicio,
          areas: areasSeleccionadas,
          conceptos,
          terminos,
          subtotal,
          iva,
          total,
          formaPago
        })
      });

      if (!response.ok) {
        throw new Error('Error al generar la orden de trabajo');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `OrdenTrabajo_${folioCompleto}.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error(error);
      alert('Hubo un problema al generar la orden de trabajo.');
    }
  });

  // Inicializar
  actualizarEstadoOtroServicio();
  actualizarTotales();
});
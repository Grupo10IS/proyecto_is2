function toggleCustomReason(select) {
    const customReasonDiv = document.getElementById('customReasonDiv');
    const customReason = document.getElementById('customReason');

    // Muestra el campo de texto solo si se selecciona "Otro"
    if (select.value === 'Otro') {
        customReasonDiv.style.display = 'block';
        customReason.value = ''; // Limpiar el campo al seleccionar "Otro"
    } else {
        customReasonDiv.style.display = 'none';
        customReason.value = ''; // Limpiar el campo si se selecciona otro motivo
    }
}

function submitReport() {
    const select = document.getElementById('reportReason');
    const customReason = document.getElementById('customReason').value;

    // Verificar que se haya seleccionado un motivo
    if (!select.value && !customReason.trim()) {
        alert('Por favor, selecciona un motivo o escribe uno.');
        return;
    }

    // Usar el motivo personalizado si se seleccionó "Otro"
    const reason = select.value === 'Otro' ? customReason : select.value;

    // Aquí puedes implementar la lógica para enviar el reporte al servidor
    console.log(`Contenido reportado por: ${reason}`);

    // Mensaje de confirmación
    alert(`Has reportado el contenido por: ${reason}`);

    // Cerrar el modal y limpiar el formulario
    document.getElementById('reportForm').reset();
    const modal = bootstrap.Modal.getInstance(document.getElementById('reportModal'));
    modal.hide();
}
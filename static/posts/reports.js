// Obtenemos las URLs y valores inyectados desde el HTML
const reportButton = document.getElementById('reportButton');
const loginUrl = reportButton.dataset.loginUrl;
const isAuthenticated = reportButton.dataset.isAuthenticated === 'true';
const reportUrl = reportButton.dataset.reportUrl;

reportButton.addEventListener('click', function () {
    if (isAuthenticated) {
        // Cargar contenido del formulario en el modal
        fetch(reportUrl)
            .then(response => {
                if (!response.ok) {

                    const existingReportModal = new bootstrap.Modal(document.getElementById('existingReportModal'));
                    existingReportModal.show();
                    // Si el status no es 2xx, mostramos el error y no continuamos
                    throw new Error(errorData.message);
                }
                return response.text(); // Si es exitoso, obtenemos el texto del formulario
            })
            .then(data => {
                // Mostrar el modal de reporte
                var reportModalElement = document.getElementById('reportModal');
                var myModal = new bootstrap.Modal(reportModalElement);
                myModal.show();
                // Inyectar el contenido del formulario en el modal
                document.getElementById('modal-body-content').innerHTML = data;

                const reasonSelect = document.getElementById('id_reason');
                if (reasonSelect) {
                    reasonSelect.addEventListener('change', function () {
                        const selectedReason = reasonSelect.value;
                        const descriptionField = document.getElementById('id_description');
                        const descriptionLabel = document.getElementById('description_label');

                        if (descriptionField && descriptionLabel) {
                            if (selectedReason === 'OTRO') {
                                descriptionField.style.display = 'block';
                                descriptionLabel.style.display = 'block';
                            } else {
                                descriptionField.style.display = 'none';
                                descriptionLabel.style.display = 'none';
                            }
                        }
                    });
                    // Ejecuta el evento 'change' una vez para manejar el estado inicial
                    reasonSelect.dispatchEvent(new Event('change'));
                }

                const reportForm = document.getElementById('reportForm');
                if (reportForm) {
                    reportForm.addEventListener('submit', function (event) {
                        event.preventDefault(); // Previene el envío normal del formulario

                        fetch(reportForm.action, {
                            method: 'POST',
                            body: new FormData(reportForm), // Envía todos los datos del formulario
                            headers: {
                                'X-CSRFToken': reportForm.querySelector('input[name="csrfmiddlewaretoken"]').value
                            }
                        })
                            .then(response => {
                                if (!response.ok) {
                                    return response.json().then(errorData => {
                                        console.error('Error al enviar el reporte:', errorData.errors);
                                        alert('Hubo un problema al enviar el reporte. Por favor, verifica los campos.');
                                    });
                                }
                                return response.json(); // Espera a que la respuesta sea convertida a JSON
                            })
                            .then(data => {
                                if (data.success) {
                                    // Cierra el modal de reporte
                                    const reportModal = bootstrap.Modal.getInstance(reportModalElement);
                                    if (reportModal) {
                                        reportModal.hide();
                                    }
                                    // Muestra el modal de éxito
                                    const successModal = new bootstrap.Modal(document.getElementById('successModal'));
                                    successModal.show();
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                            });
                    });
                } else {
                    console.error('Formulario de reporte no encontrado en el DOM.');
                }
            })
            .catch(error => {
                console.error('Reporte ya realizado o error en el envío:;', error.message);
            });

    } else {
        window.location.href = loginUrl;  // Redirige a la URL de inicio de sesión
    }
});














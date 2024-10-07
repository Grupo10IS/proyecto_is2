// Obtenemos las URLs y valores inyectados desde el HTML
const reportButton = document.getElementById('reportButton'); // Botón para reportar contenido
const loginUrl = reportButton.dataset.loginUrl; // URL de inicio de sesión
const isAuthenticated = reportButton.dataset.isAuthenticated === 'true'; // Verifica si el usuario está autenticado
const reportUrl = reportButton.dataset.reportUrl; // URL para cargar el formulario de reporte

reportButton.addEventListener('click', function () {
    // Manejador de eventos para el clic en el botón de reporte
    if (isAuthenticated) {
        // Si el usuario está autenticado, carga el contenido del formulario en el modal
        fetch(reportUrl)
            .then(response => {
                // Verifica si la respuesta es exitosa
                if (!response.ok) {
                    const existingReportModal = new bootstrap.Modal(document.getElementById('existingReportModal'));
                    existingReportModal.show(); // Muestra un modal si el reporte ya existe
                    throw new Error(errorData.message);
                }
                return response.text(); // Obtiene el texto del formulario si es exitoso
            })
            .then(data => {
                // Mostrar el modal de reporte
                var reportModalElement = document.getElementById('reportModal');
                var myModal = new bootstrap.Modal(reportModalElement);
                myModal.show(); // Muestra el modal
                // Inyectar el contenido del formulario en el modal
                document.getElementById('modal-body-content').innerHTML = data;

                // Maneja la lógica para mostrar/ocultar el campo de descripción
                const reasonSelect = document.getElementById('id_reason');
                if (reasonSelect) {
                    reasonSelect.addEventListener('change', function () {
                        const selectedReason = reasonSelect.value;
                        const descriptionField = document.getElementById('id_description');
                        const descriptionLabel = document.getElementById('description_label');

                        if (descriptionField && descriptionLabel) {
                            // Muestra el campo de descripción si la razón seleccionada es "OTRO"
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

                // Manejo del envío del formulario de reporte
                const reportForm = document.getElementById('reportForm');
                if (reportForm) {
                    reportForm.addEventListener('submit', function (event) {
                        event.preventDefault(); // Previene el envío normal del formulario

                        // Envía los datos del formulario al servidor
                        fetch(reportForm.action, {
                            method: 'POST',
                            body: new FormData(reportForm), // Envía todos los datos del formulario
                            headers: {
                                'X-CSRFToken': reportForm.querySelector('input[name="csrfmiddlewaretoken"]').value // Añade el token CSRF
                            }
                        })
                            .then(response => {
                                // Verifica si la respuesta es exitosa
                                if (!response.ok) {
                                    return response.json().then(errorData => {
                                        console.error('Error al enviar el reporte:', errorData.errors);
                                        alert('Hubo un problema al enviar el reporte. Por favor, verifica los campos.');
                                    });
                                }
                                return response.json(); // Espera a que la respuesta sea convertida a JSON
                            })
                            .then(data => {
                                // Maneja la respuesta del envío del reporte
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
        // Si el usuario no está autenticado, redirige a la URL de inicio de sesión
        window.location.href = loginUrl;
    }
});

// Función para confirmar la revisión de un post
function confirmReview(button) {
    var status = button.getAttribute('data-status'); // Obtiene el estado del post
    var url = button.getAttribute('data-url'); // Obtiene la URL para la revisión

    // Si el post ya está en revisión, mostrar el modal de "ya en revisión"
    if (status === 'Esperando revision') {
        var alreadyInReviewModal = new bootstrap.Modal(document.getElementById('alreadyInReviewModal'));
        alreadyInReviewModal.show(); // Muestra el modal correspondiente
    } else {
        // Si no, mostrar el modal de confirmación
        var confirmReviewModal = new bootstrap.Modal(document.getElementById('confirmReviewModal'));
        var confirmReviewButton = document.getElementById('confirmReviewButton');
        confirmReviewButton.setAttribute('href', url); // Cambiar el href al URL correcto
        confirmReviewModal.show();
    }
}

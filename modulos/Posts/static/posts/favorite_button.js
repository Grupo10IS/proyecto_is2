/**
 * Función para alternar el estado de la estrella (favorito o no).
 * 
 * Esta función se encarga de cambiar el estado visual de un botón
 * que representa un ítem como favorito. Al hacer clic en el botón,
 * se alterna la clase 'active', que puede cambiar su estilo (por
 * ejemplo, el color de la estrella) y se actualiza el texto del
 * tooltip que indica la acción correspondiente.
 *
 * Funcionamiento:
 * - Si el botón de estrella ya tiene la clase 'active', se la
 *   elimina, lo que indica que el ítem ya no es un favorito, y se
 *   actualiza el título del botón a "Agregar a favoritos".
 * - Si el botón de estrella no tiene la clase 'active', se le añade
 *   la clase, indicando que el ítem se ha añadido a favoritos, y se
 *   cambia el título a "Eliminar de favoritos".
 * 
 * Uso:
 * - Esta función debe ser llamada en respuesta a un evento de clic
 *   en el botón que representa el favorito (estrellas o similar).
 * 
 * Ejemplo:
 * <button id="favorite-star" onclick="toggleStar('{{ csrf_token }}')">
 *   ★
 * </button>
 * 
 * @param {string} csrftoken - El token CSRF para la protección contra ataques CSRF.
 */
function toggleStar(csrftoken) {
    const starBtn = document.getElementById('favorite-star');
    const textElement = document.getElementById('favorite-text');
    const postId = starBtn.dataset.postId; // Obtiene el ID del post desde el atributo data-post-id del botón

    fetch(`/posts/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken, // Envia el token CSRF en la cabecera
            'Content-Type': 'application/json',
        },
    }).then(response => {
        if (response.ok) {
            if (starBtn.classList.contains('active')) {
                starBtn.classList.remove('active'); // Elimina la clase 'active' si ya está presente
                starBtn.title = "Agregar a favoritos"; // Actualiza el tooltip
                textElement.textContent = 'Agregar a favoritos'; // Cambia el texto del elemento asociado
            } else {
                starBtn.classList.add('active'); // Añade la clase 'active' si no está presente
                starBtn.title = "Eliminar de favoritos"; // Actualiza el tooltip
                textElement.textContent = 'Eliminar de favoritos'; // Cambia el texto del elemento asociado
            }
        }
    });
}

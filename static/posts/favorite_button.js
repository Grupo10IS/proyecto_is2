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
 * <button id="favorite-star" onclick="toggleStar()">
 *   ★
 * </button>
 */
/*function toggleStar() {

    const starBtn = document.getElementById('favorite-star');
    const textElement = document.getElementById('favorite-text'); // Obtiene el span que contiene el texto

    if (starBtn.classList.contains('active')) {
        starBtn.classList.remove('active');
        starBtn.title = "Agregar a favoritos";
        textElement.textContent = 'Agregar a favoritos';
    }
    else {
        starBtn.classList.toggle('active');
        starBtn.title = "Eliminar de favoritos";
        textElement.textContent = 'Eliminar de favoritos';
    }

}*/
function toggleStar() {
    const starBtn = document.getElementById('favorite-star');
    const textElement = document.getElementById('favorite-text');
    const postId = starBtn.dataset.postId;

    fetch(`/posts/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    }).then(response => {
        if (response.ok) {
            if (starBtn.classList.contains('active')) {
                starBtn.classList.remove('active');
                starBtn.title = "Agregar a favoritos";
                textElement.textContent = 'Agregar a favoritos';
            } else {
                starBtn.classList.add('active');
                starBtn.title = "Eliminar de favoritos";
                textElement.textContent = 'Eliminar de favoritos';
            }
        }
    });
}

// Función para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Si este cookie string comienza con el nombre que buscamos
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


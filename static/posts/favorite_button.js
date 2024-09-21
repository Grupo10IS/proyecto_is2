// Función para alternar el estado de la estrella (favorito o no)
function toggleStar() {
    const starBtn = document.getElementById('favorite-star');
    //starBtn.classList.toggle('active');
    if (starBtn.classList.contains('active')) {
        starBtn.classList.remove('active');
        starBtn.title = "Agregar a favoritos";
    }
    else {
        starBtn.classList.toggle('active');
        starBtn.title = "Eliminar de favoritos";
    }
}
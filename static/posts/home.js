document.getElementById('search-icon').addEventListener('click', function() {
    var searchInput = document.getElementById('search-input');
    if (searchInput.style.display === 'none') {
        searchInput.style.display = 'inline-block';
        setTimeout(function() {
            searchInput.classList.add('show');
        }, 10);
    } else {
        searchInput.classList.remove('show');
        setTimeout(function() {
            searchInput.style.display = 'none';
        }, 400);  // Tiempo igual al de la transición en CSS
    }
});

window.onscroll = function() {
    var sidebar = document.querySelector('.sidebar');
    if (window.pageYOffset > 0) {
        sidebar.style.position = 'fixed';
        sidebar.style.top = '0';
    } else {
        sidebar.style.position = 'fixed';
        sidebar.style.top = '0';
    }
};



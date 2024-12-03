document.addEventListener('DOMContentLoaded', function () {
    let currentPage = 1;

    document.getElementById('load-more-button').addEventListener('click', function () {
        currentPage += 1;

        fetch(`/load_more_movies?page=${currentPage}`)
            .then((response) => response.json())
            .then((movies) => {
                const moviesContainer = document.getElementById('movies-container');
                movies.forEach((movie) => {
                    const movieCard = `
                        <div class="col-md-4">
                            <div class="card mb-4" style="width: 18rem;">
                                <img src="https://image.tmdb.org/t/p/w500${movie.poster_path}" alt="${movie.title} poster">
                                <div class="card-body">
                                    <h2 class="card-title">${movie.title}</h2>
                                    <p class="card-text">${movie.overview.slice(0, 100)}...</p>
                                    <a href="/movie/${movie.id}" class="btn bg-secondary">View Details</a>
                                </div>
                            </div>
                        </div>`;
                    moviesContainer.innerHTML += movieCard; // Append new movie cards
                });
            })
            .catch((error) => console.error('Error loading more movies:', error));
    });
});

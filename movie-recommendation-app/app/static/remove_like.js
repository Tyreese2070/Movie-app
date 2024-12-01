$(document).ready(function () {
    $(".remove-like-button").on("click", function () {
        var movieId = $(this).data("movie-id");

        $.ajax({
            url: "/remove_like",  // Define the Flask endpoint for removing from likes
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ movie_id: movieId }),
            success: function (response) {
                console.log("Movie removed from likes successfully", response);
                location.reload();  // Reload the page to update the like status
            },
            error: function (error) {
                console.log("Error removing movie from likes", error);
            },
        });
    });
});

$(document).ready(function () {
    $(".like-button").on("click", function () {
        var movieId = $(this).data("movie-id");

        $.ajax({
            url: "/like_movie",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ movie_id: movieId }),
            success: function (response) {
                console.log("Movie liked successfully", response);
                location.reload();
            },
            error: function (error) {
                console.log("Error liking movie", error);
            },
        });
    });
});

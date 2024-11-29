$(document).ready(function () {
    // Fetch reviews when the page loads
    const movieId = $('#review-form').data('movie-id');
    fetchReviews(movieId);

    function fetchReviews(movieId) {
        $.ajax({
            url: `/get_reviews/${movieId}`,
            method: "GET",
            success: function (reviews) {
                const reviewsSection = $("#reviews-section");
                reviewsSection.empty(); // Clear existing reviews

                if (reviews.length === 0) {
                    reviewsSection.append("<p>No reviews yet. Be the first to leave one!</p>");
                } else {
                    reviews.forEach((review) => {
                        reviewsSection.append(`
                            <div class="review">
                                <strong>${review.username}</strong> - ${review.rating}/10
                                <p>${review.review_text}</p>
                                <hr>
                            </div>
                        `);
                    });
                }
            },
            error: function () {
                $("#reviews-section").html("<p>Failed to load reviews. Please try again later.</p>");
            },
        });
    }

    // Handle review submission
    $("#review-form").on("submit", function (e) {
        e.preventDefault();
        const rating = $("#rating").val();
        const reviewText = $("#review_text").val();

        $.ajax({
            url: "/submit_review",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                movie_id: movieId,
                rating: rating,
                review_text: reviewText,
            }),
            success: function (response) {
                alert(response.message);
                fetchReviews(movieId); // Refresh reviews after submission
                $("#review-form")[0].reset(); // Clear the form
            },
            error: function () {
                alert("Failed to submit review. Please try again.");
            },
        });
    });
});

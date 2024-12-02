from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Movie, Review, Like
from app.forms import loginForm, signupForm, likeForm, reviewForm
import requests
from app import app, db
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_restful import Resource, Api

bcrypt = Bcrypt(app)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handles user signup.

    - GET: Displays the signup form.
    - POST: Validates the form and creates a new user in the database.
    
    Returns:
        - Validation message (successful or unsuccessful)
    """

    form = signupForm()

    if form.validate_on_submit():
        print("Validate and submit")
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Your account has been created successfully!', 'success')

        return redirect(url_for('homepage'))

    return render_template('signup.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Handles user login.

    - GET: Displays the login form.
    - POST: Validates the form and authenticates the user so they can access the homepage.
    
    Parameters:
        None

    Returns:
        - Sends the user to homepage upon success
        - Error message if unsuccessful
    """
    
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    form = loginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('homepage'))
        else:
            flash('Incorrect username or password', 'danger')
    
    return render_template('login.html', form=form)
    
@app.route('/logout')
@login_required
def logout():
    """
    Logs the user out of the system.
    
    Parameters:
        None

    Returns:
        - Returns the user to the login page
    """
    
    logout_user()
    flash('You have been logged out.', 'info')
    
    return redirect(url_for('login'))


# Use of TMDb API to get movie data and some filtering, found at: https://developer.themoviedb.org/docs/getting-started
KEY = 'REMOVED'
URL = 'https://api.themoviedb.org/3'

@app.route('/homepage')
@login_required
def homepage():
    """
    Displays movies for the user to see.
    """
    url = f'{URL}/movie/popular?api_key={KEY}'
    response = requests.get(url)
    data = response.json()
    movies = data.get('results', [])
    for movie_data in movies:
        existing_movie = Movie.query.filter_by(id=movie_data['id']).first()
        if not existing_movie:
            release_date = datetime.strptime(movie_data['release_date'], "%Y-%m-%d").date()

            new_movie = Movie(
                id=movie_data['id'],
                title=movie_data['title'],
                genre=', '.join(str(genre_id) for genre_id in movie_data.get('genre_ids', [])),
                release_date=release_date,
                poster_path=movie_data.get('poster_path'),
                overview=movie_data['overview']
            )
            db.session.add(new_movie)
    db.session.commit()

    return render_template('homepage.html', movies=movies)

@app.route('/like_movie', methods=['POST'])
@login_required
def like_movie():
    data = request.get_json()
    movie_id = data.get("movie_id")

    movie = Movie.query.get_or_404(movie_id)

    existing_like = Like.query.filter_by(user_id=current_user.id, movie_id=movie.id).first()
    if not existing_like:
        like = Like(user_id=current_user.id, movie_id=movie.id)
        db.session.add(like)
        db.session.commit()
        print("liked movie")

    return jsonify({"status": "success", "message": f"You liked {movie.title}"})


@app.route('/remove_like', methods=['POST'])
@login_required
def remove_like():
    data = request.get_json()
    movie_id = data.get("movie_id")

    # Fetch the movie from the database
    movie = Movie.query.get_or_404(movie_id)

    # Check if the user has liked the movie
    existing_like = Like.query.filter_by(user_id=current_user.id, movie_id=movie.id).first()

    if existing_like:
        # Remove the like from the database
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({"status": "success", "message": f"{movie.title} removed from liked movies"})
    else:
        return jsonify({"status": "error", "message": "Movie not found in your liked list"})


@app.route('/dashboard')
@login_required
def dashboard():
    """
    Displays the user's dashboard with their username, liked movies, and AJAX functionality.
    """
    # Fetch the logged-in user
    user = current_user

    # Get the movies the user has liked
    liked_movies = (
        db.session.query(Movie)
        .join(Like, Movie.id == Like.movie_id)
        .filter(Like.user_id == user.id)
        .order_by(Movie.release_date.desc())  # Order by most recent first
        .all()
    )

    # Pass user and liked movies to the template
    return render_template(
        'dashboard.html',
        username=user.username,
        liked_movies=liked_movies,  # Send liked movies to the template
    )




@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    Handles user settings updates (username and password).

    - GET: Displays the settings form.
    - POST: Validates the form and updates the user's information in the database.

    Returns:
        - A success or failure message based on the form validation and submission.
    """
    # Initialize form with FlaskForm structure
    form = signupForm()

    if form.validate_on_submit():
        # Fetch the current user
        user = current_user

        # Handle username update
        if form.username.data and form.username.data != user.username:
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'danger')
                return redirect(url_for('settings'))
            else:
                user.username = form.username.data
                db.session.commit()
                flash('Username updated successfully!', 'success')

        # Handle password update
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Password updated successfully!', 'success')

    return render_template('settings.html', form=form)



@app.route('/movie/<int:movie_id>')
@login_required
def movie(movie_id):
    """
    Displays the movie details and handles liking and reviewing.
    """
    # Query the movie from the database using the movie_id
    movie = Movie.query.get_or_404(movie_id)

    # Query for the movies liked by the current user
    liked_movies = {like.movie_id for like in current_user.likes}

    # Forms for liking and reviewing
    like_form = likeForm()
    review_form = reviewForm()

    # Handle liking the movie
    if like_form.validate_on_submit() and like_form.submit.data:
        flash(f'You liked {movie.title}!', 'success')
        # Handle liking functionality (e.g., save in DB, optional feature)
        return redirect(url_for('movie', movie_id=movie.id))

    # Handle submitting a review
    if review_form.validate_on_submit() and review_form.submit.data:
        new_review = Review(
            user_id=current_user.id,
            movie_id=movie.id,
            rating=review_form.rating.data,
            review_text=review_form.review_text.data
        )
        db.session.add(new_review)
        db.session.commit()
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('movie', movie_id=movie.id))

    return render_template(
        'movie.html',
        movie=movie,
        like_form=like_form,
        review_form=review_form,
        liked_movies=liked_movies
    )

@app.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    data = request.get_json()
    movie_id = data.get("movie_id")
    rating = data.get("rating")
    review_text = data.get("review_text")

    # Validate the movie
    movie = Movie.query.get_or_404(movie_id)

    # Save the review
    new_review = Review(
        user_id=current_user.id,
        movie_id=movie.id,
        rating=rating,
        review_text=review_text,
    )
    db.session.add(new_review)
    db.session.commit()

    return jsonify({"status": "success", "message": "Review submitted successfully"})

@app.route('/get_reviews/<int:movie_id>', methods=['GET'])
@login_required
def get_reviews(movie_id):
    """
    Fetches reviews for a specific movie.
    """
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie.id).all()
    review_list = [
        {
            "username": review.user.username,  # Assuming the Review model has a relationship with User
            "rating": review.rating,
            "review_text": review.review_text,
        }
        for review in reviews
    ]
    return jsonify(review_list)

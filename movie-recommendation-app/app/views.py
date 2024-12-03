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
    Handles user signup form with case-insensitive username check.
    """
    
    form = signupForm()

    if form.validate_on_submit():
        print("Validate and submit")

        # Check if the username already exists - use of ilike so it's case insensitive
        existing_user = User.query.filter(User.username.ilike(form.username.data)).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))

        # Hash the password and create new user
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        username = form.username.data.lower()
        new_user = User(username=username, password=hashed_password)

        # Add the user to the database and commit
        db.session.add(new_user)
        db.session.commit()

        # Log the user in and redirect to homepage
        login_user(new_user)
        flash('Your account has been created successfully!', 'success')

        return redirect(url_for('homepage'))

    return render_template('signup.html', form=form)

@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    form = loginForm()

    # Check if information is correct and redirect
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
    """
    
    logout_user()
    flash('You have been logged out.', 'info')
    
    return redirect(url_for('login'))


# Use of TMDb API to get movie data found at: https://developer.themoviedb.org/docs/getting-started
KEY = 'REMOVED'
URL = 'https://api.themoviedb.org/3'

@app.route('/homepage')
@login_required
def homepage():
    """
    Displays movies for the user to see.
    """
    
    # Getting the data from the API site
    url = f'{URL}/movie/popular?api_key={KEY}'
    response = requests.get(url)
    data = response.json()
    movies = data.get('results', [])
    
    # Going through each movie and storing the relevant data for like/reviewing purposes
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

@app.route('/load_more_movies', methods=['GET'])
@login_required
def load_more_movies():
    """
    Loads more movies when the button is pressed.
    """
    # Requesting data with the API
    page = request.args.get('page', 1, type=int)
    url = f'{URL}/movie/popular?api_key={KEY}&page={page}'
    response = requests.get(url)
    data = response.json()
    movies = data.get('results', [])

    # Storing movie data
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

    # Return for AJAX use
    return jsonify(movies)

@app.route('/search', methods=['GET'])
@login_required
def search():
    """
    Handles search query when search button is pressed
    """
    
    # Get the input
    query = request.args.get('search', '').strip()
    results = []

    if query:
        # Fetch results from API
        tmdb_url = f'{URL}/search/movie?api_key={KEY}&query={query}'
        response = requests.get(tmdb_url)
        if response.status_code == 200:
            api_data = response.json()
            results = api_data.get('results', [])

            # Add movies to the database
            for movie_data in results:
                existing_movie = Movie.query.filter_by(id=movie_data['id']).first()
                if not existing_movie:
                    # Handle the release_date if it's empty or invalid - Common error when searching
                    release_date_str = movie_data.get('release_date', '')
                    release_date = None
                    if release_date_str:
                        try:
                            release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
                        except ValueError:
                            release_date = None

                    # Add new movie to the database with a valid release_date
                    new_movie = Movie(
                        id=movie_data['id'],
                        title=movie_data['title'],
                        genre=', '.join(str(genre_id) for genre_id in movie_data.get('genre_ids', [])),
                        release_date=release_date or datetime(1900, 1, 1).date(), # Giving a default release date if none found
                        poster_path=movie_data.get('poster_path'),
                        overview=movie_data['overview']
                    )
                    db.session.add(new_movie)
            db.session.commit()

        else:
            flash('Failed to fetch search results from TMDb.', 'danger')

    return render_template('search_results.html', query=query, results=results)

@app.route('/like_movie', methods=['POST'])
@login_required
def like_movie():
    """
    Handles like feature, adds the user id and movie to the like database
    """
    
    # Getting relevant data to store the like
    data = request.get_json()
    movie_id = data.get("movie_id")
    movie = Movie.query.get_or_404(movie_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, movie_id=movie.id).first() # Checks if already liked by user
    
    # Adding the like to the database
    if not existing_like:
        like = Like(user_id=current_user.id, movie_id=movie.id)
        db.session.add(like)
        db.session.commit()
        print("liked movie")

    return jsonify({"status": "success", "message": f"You liked {movie.title}"})

@app.route('/remove_like', methods=['POST'])
@login_required
def remove_like():
    """
    Removes a like from the like database
    """
    
    # Get relevant data
    data = request.get_json()
    movie_id = data.get("movie_id")
    movie = Movie.query.get_or_404(movie_id)

    existing_like = Like.query.filter_by(user_id=current_user.id, movie_id=movie.id).first()

    # Remove like from database
    if existing_like:
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
    
    # Get username for personalised message
    user = current_user

    # Get the movies the user has liked
    liked_movies = (
        db.session.query(Movie)
        .join(Like, Movie.id == Like.movie_id)
        .filter(Like.user_id == user.id)
        .order_by(Movie.release_date.desc())  # Order by most recent first
        .all()
    )

    return render_template(
        'dashboard.html',
        username=user.username,
        liked_movies=liked_movies,
    )

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    Handles user settings updates (username, password, darkmode).
    """
    form = signupForm()

    if form.validate_on_submit():
        user = current_user

        # Check if username already exists
        if form.username.data and form.username.data != user.username:
            existing_user = User.query.filter(User.username.ilike(form.username.data)).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'danger')
                return redirect(url_for('settings'))
            else:
                # Change username if it doesn't exist
                user.username = form.username.data.lower()
                db.session.commit()
                flash('Username updated successfully!', 'success')

        # Update password
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

    # Get relevant data to display
    movie = Movie.query.get_or_404(movie_id)
    liked_movies = {like.movie_id for like in current_user.likes}
    like_form = likeForm()
    review_form = reviewForm()

    # Movie like button
    if like_form.validate_on_submit() and like_form.submit.data:
        flash(f'You liked {movie.title}!', 'success')
        return redirect(url_for('movie', movie_id=movie.id))

    # Review text area / button
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
    """
    Handles review form submission
    """
    
    # Get relevant data for the form
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
    Gets reviews for a specific movie.
    """
    
    # Check the review database for movies, then return them as a list
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie.id).all()
    review_list = [
        {
            "username": review.user.username,
            "rating": review.rating,
            "review_text": review.review_text,
        }
        for review in reviews
    ]
    return jsonify(review_list)

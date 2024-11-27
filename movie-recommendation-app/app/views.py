from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.forms import loginForm
from app.forms import signupForm
import requests
from app import app, db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handles user signup.

    - GET: Displays the signup form.
    - POST: Validates the form and creates a new user in the database.
    
    Parameters:
        None

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

    Returns:
        - homepage template
    """

    url = f'{URL}/movie/popular?api_key={KEY}'
    response = requests.get(url)
    data = response.json()

    movies = data.get('results', [])

    return render_template('homepage.html', movies=movies)

@app.route('/likes')
@login_required
def likes():
    """
    Displays users liked movies.

    Returns:
        - 
    """
    
    return render_template('likes.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Displays users information.

    Returns:
        - 
    """
    return render_template('dashboard.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/movie')
@login_required
def movie():
    return render_template('movie.html')
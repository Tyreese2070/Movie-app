from app import app, db
from app.models import User

# Use app.app_context() to ensure we're within an application context
with app.app_context():
    # Create a new user
    user = User(username='testuser')
    user.set_password('password123')  # Set the hashed password
    db.session.add(user)
    db.session.commit()

    print("User created successfully")

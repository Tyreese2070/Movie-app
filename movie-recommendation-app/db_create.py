#from config import SQLALCHEMY_DATABASE_URI
#from app import db
#import os.path

#db.create_all()

from app import app, db
from app.models import User, Movie, Review

with app.app_context():
    db.create_all()
    print("Database created")

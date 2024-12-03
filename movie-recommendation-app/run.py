from app import app
from app import db

#if __name__ == '__main__':
#    app.run(debug=True)
    
from socket import gethostname

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    if 'liveconsole' not in gethostname():
        app.run()
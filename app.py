from flask import Flask
from flask_sqlalchemy import SQLAlchemy # For database handling
import os # For getting the enviromental variable

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('DATABASE_KEY', 'obraz_szklanka_szafa')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db" # it means in folder named "instance"
db = SQLAlchemy(app)

from routes import *

if __name__ == '__main__':
    with app.app_context(): # If there's no data.db create one
        db.create_all()
    app.run(debug=True)

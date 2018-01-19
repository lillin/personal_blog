from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .momentjs import momentjs


app = Flask(__name__)
app.config.from_object('config')  # tell Flask to read config.py
app.jinja_env.globals['momentjs'] = momentjs  # tell Jinja2 to expose our class as a global variable to all templates

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


from app import views

from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    from app.auth import auth_bp
    from app.smm import smm_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(smm_bp, url_prefix='/smm')

    @app.route('/')
    def index():
        return redirect(url_for('smm.dashboard'))

    return app

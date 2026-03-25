from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense_splitter.db'
    db.init_app(app)
    from app.models import Usuario, Grupo, Gasto
    with app.app_context():
        db.create_all()

    from app.main import bp
    app.register_blueprint(bp)
    
    return app
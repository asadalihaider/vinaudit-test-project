from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from app.config.config import Config


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    cors = CORS(app, resources={r"*": {"origins": "*"}})

    app.config.from_object(Config)

    db.init_app(app)

    @app.route("/")
    def root():
        return "Hello VinAudit!"

    # Import the routes AFTER initializing db to avoid circular imports
    from app.routes.car_routes import car_bp
    app.register_blueprint(car_bp)

    return app

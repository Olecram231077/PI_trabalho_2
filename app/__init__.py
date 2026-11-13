import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def create_app(config_name=None):
    app = Flask(__name__)

    from app.config import config_by_name
    env = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_by_name.get(env, config_by_name['development']))

    db.init_app(app)

    from app.routes.views import views_bp
    from app.routes.api import api_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    @app.errorhandler(404)
    def not_found(error):
        from flask import jsonify, request
        if request.path.startswith('/api/'):
            return jsonify({'erro': 'Recurso não encontrado'}), 404
        return error, 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import jsonify, request
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'erro': 'Erro interno do servidor'}), 500
        return error, 500

    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()


    return app
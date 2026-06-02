import os
from flask import Flask, jsonify
from config import config
from models import db
from controllers.employee_controller import employee_bp


def create_app(config_name=None):
    """Application factory"""
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    if app.config.get('ENV') != 'production':
        with app.app_context():
            db.create_all()

    app.register_blueprint(employee_bp)

    @app.route('/')
    def home():
        return jsonify({
            "message": "Employee Management System API",
            "endpoints": {
                "POST /employees": "Add a new employee",
                "GET /employees": "Get all employees",
                "GET /employees/<id>": "Get employee by ID",
                "PUT /employees/<id>": "Update employee",
                "DELETE /employees/<id>": "Delete employee"
            }
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )

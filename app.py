import os
import sys
import argparse
from flask import Flask, jsonify
from core.config import Config
from core.db import init_db_connections
from models.employee_model import db
from controllers.employee_controller import employee_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    init_db_connections(app)

    with app.app_context():
        # setup tables on master
        db.create_all()
        
        # try to setup on replica just in case
        from core.db import replica_engine
        if replica_engine:
            try:
                db.metadata.create_all(bind=replica_engine)
            except Exception as e:
                app.logger.warning(
                    f"Couldn't run migration on replica (might be read-only): {e}"
                )

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
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    if args.test:
        from tests.test_runner import run_tests
        exit_code = run_tests()
        sys.exit(exit_code)
    else:
        app = create_app()
        app.run(
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000)),
            debug=app.config.get('DEBUG', True)
        )

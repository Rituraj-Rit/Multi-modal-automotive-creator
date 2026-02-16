try:
    from flask import Flask, render_template, send_from_directory
    from flask_cors import CORS
except Exception as e:
    print("Missing required Python packages:", e)
    print("Please install project dependencies: `pip install -r requirements.txt`")
    raise

from src.config import get_config
from src.api.routes import visualization_bp
import os


def create_app():
    """
    Application factory function.
    Creates and configures the Flask application.
    """
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static')
    )
    
    # Load configuration
    config = get_config()
    app.config['SECRET_KEY'] = config.SECRET_KEY
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(visualization_bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Endpoint not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    # Serve frontend
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory(app.static_folder, path)
    
    return app


if __name__ == '__main__':
    app = create_app()
    config = get_config()
    app.run(
        host=config.APP_HOST,
        port=config.APP_PORT,
        debug=config.FLASK_DEBUG
    )

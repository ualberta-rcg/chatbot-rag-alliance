import os
import sys  
import signal
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from config import Config
from models import db 
from utils.logger import setup_logger
from utils.managers.handler_manager import HandlerManager
from utils.handlers import SocketIOCallbackHandler
from routes.routes import configure_routes  
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_socketio import SocketIO
from flask_session import Session
from gevent import monkey
monkey.patch_all()

def check_env_vars():
    """Ensure all required environment variables are set."""
    required_vars = [
        'SECRET_KEY',
        'AI_MODEL_A',
        'AI_MODEL_B',        
        'AI_PROVIDER'
    ]
    for var in required_vars:
        if not os.getenv(var):
            print(f"Error: {var} is not defined. Exiting.")
            sys.exit(1)  # Stop the app if any required var is missing

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    app.config['SITEMAP_URL_SCHEME'] = 'https'
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Allow cross-origin requests 
    app.config['SESSION_COOKIE_SECURE'] = True      # Ensure cookies are sent over HTTPS
    app.config['SESSION_PERMANENT'] = True          # Sessions Exist If Browser Close
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)  # Set session lifetime to 3 days

    # Configure server-side session storage
    app.config['SESSION_TYPE'] = 'filesystem'

    csrf = CSRFProtect(app)
    
    # Initialize Flask-Session
    Session(app)
    
    # Initialize Extensions
    db.init_app(app)

    # Setup logging
    logger = setup_logger('app_logger', app.config['LOG_LEVEL'])
    app.logger = logger  # Set Flask's logger to the custom logger

    # Initialize Flask-SocketIO
    socketio = SocketIO(
        app, 
        manage_session=False, 
        cors_allowed_origins="*", 
        ping_timeout=600, 
        ping_interval=60, 
        async_mode='gevent', 
        logger=True, 
        engineio_logger=True
    )

    # Attach HandlerManager to the app
    app.handler_manager = HandlerManager()
    
    # Create tables if they do not exist
    with app.app_context():
        db.create_all()
        
    # Configure routes (including WebSocket routes)
    configure_routes(app, socketio)
   
    return app, socketio

# Check if required environment variables are set
check_env_vars()
app, socketio = create_app()


if __name__ == '__main__':
    # Use socketio.run() for development; use a WSGI server (e.g., Gunicorn with gevent) for production
    socketio.run(app)

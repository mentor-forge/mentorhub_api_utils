# api_utils/__init__.py
from .config.config import Config
from .flask_utils.breadcrumb import create_flask_breadcrumb
from .flask_utils.token import Token, create_flask_token
from .flask_utils.exceptions import HTTPUnauthorized, HTTPForbidden, HTTPNotFound, HTTPInternalServerError
from .flask_utils.route_wrapper import handle_route_exceptions
from .flask_utils.ejson_encoder import MongoJSONEncoder
from .mongo_utils.mongo_io import MongoIO
from .mongo_utils.encode_properties import encode_document
from .routes.config_routes import create_config_routes
from .routes.metric_routes import create_metric_routes
from .routes.explorer_routes import create_explorer_routes

# Import server app for direct use (lazy import to avoid MongoDB connection on import)
# The app can be imported without requiring MongoDB to be running
try:
    from .server import app
except Exception as e:
    # Server may not be available if dependencies are missing or MongoDB connection fails
    # This is OK for testing and when MongoDB isn't required
    import logging
    logging.getLogger(__name__).debug(f"Server app not available: {e}")
    app = None

__all__ = [
    # Configuration and Database Utilities
    Config, MongoIO, MongoJSONEncoder, encode_document,

    # Flask Utility Functions
    create_flask_breadcrumb, Token, create_flask_token,
    HTTPUnauthorized, HTTPForbidden, HTTPNotFound, HTTPInternalServerError,
    handle_route_exceptions,
    
    # Route Blueprints
    create_config_routes,
    create_metric_routes,
    create_explorer_routes,
    
    # Demo Server
    "app",
]


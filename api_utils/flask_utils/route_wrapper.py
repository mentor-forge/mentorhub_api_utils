"""
Flask route wrapper utility for exception handling.

Provides a decorator that automatically converts custom HTTP exceptions
to appropriate Flask responses with correct status codes and error messages.
"""

from functools import wraps
from flask import jsonify
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPUnauthorized,
    HTTPForbidden,
    HTTPNotFound,
    HTTPInternalServerError,
)
import logging

logger = logging.getLogger(__name__)


def handle_route_exceptions(f):
    """
    Decorator to handle custom HTTP exceptions in Flask routes.
    
    This wrapper automatically converts custom exceptions to appropriate
    JSON responses with the correct HTTP status codes:
    - HTTPBadRequest -> 400
    - HTTPUnauthorized -> 401
    - HTTPForbidden -> 403
    - HTTPNotFound -> 404
    - HTTPInternalServerError -> 500
    - Other exceptions -> 500 (with generic error message)
    
    Args:
        f: The Flask route function to wrap
        
    Returns:
        The wrapped function with exception handling
        
    Example:
        @app.route('/api/example')
        @handle_route_exceptions
        def example_route():
            # Your route logic here
            if not authenticated:
                raise HTTPUnauthorized("Invalid token")
            return jsonify({"data": "success"})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HTTPBadRequest as e:
            logger.warning(f"HTTPBadRequest: {e.message}")
            return jsonify({"error": e.message}), e.status_code
        except HTTPUnauthorized as e:
            logger.warning(f"HTTPUnauthorized: {e.message}")
            return jsonify({"error": e.message}), e.status_code
        except HTTPForbidden as e:
            logger.warning(f"HTTPForbidden: {e.message}")
            return jsonify({"error": e.message}), e.status_code
        except HTTPNotFound as e:
            logger.info(f"HTTPNotFound: {e.message}")
            return jsonify({"error": e.message}), e.status_code
        except HTTPInternalServerError as e:
            logger.error(f"HTTPInternalServerError: {e.message}")
            return jsonify({"error": e.message}), e.status_code
        except Exception as e:
            logger.error(f"Unexpected error in route {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({"error": "A processing error occurred"}), 500
    return decorated_function


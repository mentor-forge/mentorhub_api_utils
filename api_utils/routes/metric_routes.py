"""
Prometheus Metrics routes for Flask services.

Provides a factory function to configure Prometheus metrics middleware.
This middleware automatically exposes a /metrics endpoint for Prometheus scraping.
"""
from prometheus_flask_exporter import PrometheusMetrics
import logging

logger = logging.getLogger(__name__)


def create_metric_routes(app):
    """
    Create and configure Prometheus metrics middleware for a Flask app.
    
    IMPORTANT: This is middleware, NOT a Flask Blueprint. 
    - Do NOT use app.register_blueprint() with this function
    - The PrometheusMetrics class wraps the Flask app directly as middleware
    - It automatically exposes a /metrics endpoint (no blueprint registration needed)
    - Returns a PrometheusMetrics object, not a Blueprint
    
    Args:
        app: Flask application instance
        
    Returns:
        PrometheusMetrics: The configured metrics object (for potential future use)
        
    Example usage:
        from api_utils import create_metric_routes
        metrics = create_metric_routes(app)  # Not app.register_blueprint(...)
    """
    metrics = PrometheusMetrics(app)
    logger.info("Prometheus metrics middleware configured - /metrics endpoint available")
    return metrics


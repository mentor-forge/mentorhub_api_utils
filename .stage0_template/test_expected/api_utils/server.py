"""
Demo Server for api_utils

This is a demonstration server that showcases the utilities provided by the api_utils package:
- Config singleton for configuration management
- MongoIO singleton for MongoDB operations
- Flask routes for config endpoint
- Health endpoint for Prometheus monitoring

This demonstration server showcases the utilities provided by the api_utils package:
- Config singleton for configuration management
- MongoIO singleton for MongoDB operations
- Flask routes for config endpoint
- Prometheus metrics endpoint

This server is designed for:
- Demonstrating package usage
- Black-box testing of the utilities
- Integration testing scenarios

The server provides:
- `/api/config` - Configuration endpoint
- `/metrics` - Prometheus metrics endpoint
"""
import sys
import signal
from flask import Flask

# Initialize Config Singleton (doesn't require external services)
from api_utils import Config
config = Config.get_instance()

# Initialize logging (Config constructor configures logging)
import logging
logger = logging.getLogger(__name__)
logger.info("============= Starting api_utils Demo Server ===============")

# Initialize MongoIO Singleton and set enumerators and versions
from api_utils import MongoIO
mongo = MongoIO.get_instance()
config.set_enumerators(mongo.get_documents(config.ENUMERATORS_COLLECTION_NAME))
config.set_versions(mongo.get_documents(config.VERSIONS_COLLECTION_NAME))

# Initialize Flask App
from api_utils import MongoJSONEncoder
app = Flask(__name__)
app.json = MongoJSONEncoder(app)

# Route registration (all grouped together)
from api_utils import (
    create_metric_routes,
    create_explorer_routes,
    create_config_routes
)

# Register route blueprints
app.register_blueprint(create_explorer_routes(), url_prefix='/docs')
app.register_blueprint(create_config_routes(), url_prefix='/api/config')
metrics = create_metric_routes(app) # This exposes /metrics endpoint

logger.info("============= Routes Registered ===============")
logger.info("  /docs/<path> - API Explorer")
logger.info("  /api/config - Configuration endpoint")
logger.info("  /metrics - Prometheus metrics endpoint")

# Define a signal handler for SIGTERM and SIGINT
def handle_exit(signum, frame):
    """Handle graceful shutdown on SIGTERM/SIGINT."""
    global mongo
    logger.info(f"Received signal {signum}. Initiating shutdown...")
    
    # Disconnect from MongoDB if connected
    if mongo is not None:
        logger.info("Closing MongoDB connection.")
        try:
            mongo.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting from MongoDB: {e}")
    
    logger.info("Shutdown complete.")
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

# Expose app for Gunicorn or direct execution
if __name__ == "__main__":
    logger.info(f"Starting Flask server on port {config.COMMON_CODE_API_PORT}")
    app.run(host="0.0.0.0", port=config.COMMON_CODE_API_PORT, debug=False)

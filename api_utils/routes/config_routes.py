from flask import Blueprint, jsonify
from api_utils.config.config import Config
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions

import logging
logger = logging.getLogger(__name__)

# Define the Blueprint for config routes
def create_config_routes():
    config_routes = Blueprint('config_routes', __name__)
    config = Config.get_instance()
    
    # GET /api/config - Return the current configuration as JSON
    @config_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_config():
        # Return the JSON representation of the config object
        # Token is automatically validated by create_flask_token()
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        logger.info(f"get_config Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(config.to_dict(token)), 200
        
    logger.info("Config Flask Routes Registered")
    return config_routes


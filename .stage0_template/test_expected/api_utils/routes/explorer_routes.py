"""
API Explorer routes for Flask services.

Provides a factory function to serve static API explorer files from a docs directory.
This is typically used to serve OpenAPI/Swagger documentation.
"""
import os
from flask import Blueprint, send_from_directory
import logging

logger = logging.getLogger(__name__)


def create_explorer_routes(docs_dir=None):
    """
    Create a Flask Blueprint to serve static API explorer files.
    
    Args:
        docs_dir (str, optional): Path to the docs directory. 
                                  Defaults to 'docs/' relative to project root.
                                  If None, will attempt to find docs/ relative to the calling file.
        
    Returns:
        Blueprint: Flask Blueprint with route to serve static files
        
    Example usage:
        from api_utils import create_explorer_routes
        app.register_blueprint(create_explorer_routes(), url_prefix='/docs')
        
        # Or with custom docs directory:
        app.register_blueprint(create_explorer_routes(docs_dir='/path/to/docs'), url_prefix='/docs')
    """
    explorer_routes = Blueprint('explorer_routes', __name__)
    
    # If docs_dir not provided, try to find it relative to project root
    if docs_dir is None:
        # Get the directory where this file is located, then go up to project root
        # This assumes the structure: project_root/api_utils/routes/explorer_routes.py
        current_file = os.path.abspath(__file__)
        # Go up from api_utils/routes/explorer_routes.py to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        docs_dir = os.path.join(project_root, 'docs')
    
    # Ensure docs_dir is absolute
    docs_dir = os.path.abspath(docs_dir)
    
    @explorer_routes.route('/<path:filename>')
    def serve_docs(filename):
        """Serve static files from the docs directory."""
        return send_from_directory(docs_dir, filename)
    
    logger.info(f"API Explorer routes registered - serving from {docs_dir}")
    return explorer_routes


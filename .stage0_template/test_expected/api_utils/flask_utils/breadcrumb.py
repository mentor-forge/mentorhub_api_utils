from datetime import datetime, timezone
import uuid
from flask import request

def create_flask_breadcrumb(token):
    """Create a breadcrumb dictionary from HTTP headers."""
    return {
        "at_time": datetime.now(timezone.utc),
        "by_user": token["user_id"],
        "from_ip": request.remote_addr,  
        "correlation_id": request.headers.get('X-Correlation-Id', str(uuid.uuid4()))  
    }


"""
Custom HTTP exceptions for Flask routes.

These exceptions are used to handle different HTTP error scenarios:
- 400 Bad Request: Invalid request parameters
- 401 Unauthorized: Authentication failed
- 403 Forbidden: Authorization failed
- 404 Not Found: Resource not found
- 500 Internal Server Error: Processing errors
"""


class HTTPBadRequest(Exception):
    """
    Exception for 400 Bad Request errors.
    
    Raised when request parameters are invalid or malformed.
    """
    status_code = 400
    message = "Bad Request"

    def __init__(self, message=None):
        if message:
            self.message = message
        super().__init__(self.message)


class HTTPUnauthorized(Exception):
    """
    Exception for 401 Unauthorized errors.
    
    Raised when authentication fails (e.g., missing or invalid token).
    """
    status_code = 401
    message = "Unauthorized"

    def __init__(self, message=None):
        if message:
            self.message = message
        super().__init__(self.message)


class HTTPForbidden(Exception):
    """
    Exception for 403 Forbidden errors.
    
    Raised when authorization fails (e.g., insufficient permissions).
    """
    status_code = 403
    message = "Forbidden"

    def __init__(self, message=None):
        if message:
            self.message = message
        super().__init__(self.message)


class HTTPNotFound(Exception):
    """
    Exception for 404 Not Found errors.
    
    Raised when a requested resource cannot be found.
    """
    status_code = 404
    message = "Not Found"

    def __init__(self, message=None):
        if message:
            self.message = message
        super().__init__(self.message)


class HTTPInternalServerError(Exception):
    """
    Exception for 500 Internal Server Error.
    
    Raised when an unexpected processing error occurs.
    """
    status_code = 500
    message = "Internal Server Error"

    def __init__(self, message=None):
        if message:
            self.message = message
        super().__init__(self.message)


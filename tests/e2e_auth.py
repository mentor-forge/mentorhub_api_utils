"""Bearer JWT for E2E tests against the demo server.

Must match ``JWT_SECRET`` used when running the API locally. Developer Edition and ``pipenv run dev``
default to ``local-dev-jwt-secret-fixed`` (same secret as ``welcome-auth.js`` / ``login.html``).
Claims: iss ``dev-idp``, aud ``dev-api``; subject ``adam`` with role ``admin`` (E2E persona).
``profile_id`` is required by :func:`api_utils.flask_utils.token.create_flask_token`.
"""

from __future__ import annotations

import os
import time

import jwt

_DEFAULT_JWT_SECRET = "local-dev-jwt-secret-fixed"
_DEFAULT_JWT_ISSUER = "dev-idp"
_DEFAULT_JWT_AUDIENCE = "dev-api"
_DEFAULT_JWT_ALGORITHM = "HS256"

_E2E_SUBJECT = "adam"
_E2E_NAME = "Adam (E2E)"
_E2E_ROLES = ("admin",)
_E2E_PROFILE_ID = "A00000000000000000000001"
_E2E_CUSTOMER_ID = "D00000000000000000000006"
_E2E_MENTOR_ID = ""


def get_auth_token() -> str:
    """Mint a long-lived admin persona JWT for black-box tests."""
    # Use E2E_* overrides so unit-test conftest JWT_SECRET does not affect the dev server.
    secret = os.environ.get("E2E_JWT_SECRET") or _DEFAULT_JWT_SECRET
    issuer = os.environ.get("E2E_JWT_ISSUER") or _DEFAULT_JWT_ISSUER
    audience = os.environ.get("E2E_JWT_AUDIENCE") or _DEFAULT_JWT_AUDIENCE
    algorithm = os.environ.get("E2E_JWT_ALGORITHM") or _DEFAULT_JWT_ALGORITHM
    now = int(time.time())
    payload = {
        "iss": issuer,
        "aud": audience,
        "sub": _E2E_SUBJECT,
        "name": _E2E_NAME,
        "iat": now,
        "exp": now + 10 * 365 * 24 * 60 * 60,
        "roles": list(_E2E_ROLES),
        "profile_id": _E2E_PROFILE_ID,
        "customer_id": _E2E_CUSTOMER_ID,
        "mentor_id": _E2E_MENTOR_ID,
    }
    token = jwt.encode(payload, secret, algorithm=algorithm)
    if isinstance(token, bytes):
        return token.decode("ascii")
    return token

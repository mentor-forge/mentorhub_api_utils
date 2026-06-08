"""Static bearer JWT for E2E tests against the demo server.

Must match ``JWT_SECRET`` used when running the API locally. Developer Edition and ``pipenv run dev``
default to ``local-dev-jwt-secret-fixed``. Same string as welcome ``index.html`` TOKEN_ADAM.
Claims: iss ``dev-idp``, aud ``dev-api``; subject ``adam`` with role ``admin``.
"""

E2E_ACCESS_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkZXYtaWRwIiwiYXVkIjoiZGV2LWFwaSIsInN1YiI6ImFkYW0iLCJpYXQiOjE3NzQ1NTMwNTEsImV4cCI6MjA4OTkxMzA1MSwicm9sZXMiOlsiYWRtaW4iXX0.S_Vxouja_C6kshlUyiU8sqiVGrpAIl3oSMxwNRUNDIQ"
)


def get_auth_token() -> str:
    return E2E_ACCESS_TOKEN

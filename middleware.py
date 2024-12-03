from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from msal import ConfidentialClientApplication, SerializableTokenCache
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read values from the .env file
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SCOPES = os.getenv("SCOPES", "https://graph.microsoft.com/.default").split(",")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

# Token cache for MSAL
token_cache = SerializableTokenCache()

# Initialize MSAL application
msal_app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
    token_cache=token_cache,
)

# Custom middleware for Azure AD authentication
class AzureAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Missing or invalid Authorization header")
            return JSONResponse(
                status_code=401,
                content={"error": "Missing or invalid Authorization header"},
                headers={"WWW-Authenticate": 'Bearer realm="example.com"'},
            )

        token = auth_header.split("Bearer ")[1]
        try:
            # Validate the token with MSAL
            result = msal_app.acquire_token_for_client(scopes=SCOPES)
            if not result or "access_token" not in result:
                logger.error(f"Token validation failed: {result.get('error_description', 'Invalid token')}")
                raise Exception(result.get("error_description", "Invalid token"))
        except Exception as e:
            logger.exception("Unauthorized access attempt")
            return JSONResponse(
                status_code=401,
                content={"error": f"Unauthorized: {str(e)}"},
                headers={"WWW-Authenticate": 'Bearer realm="example.com"'},
            )

        logger.info("Token validated successfully")
        response = await call_next(request)
        return response

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import os
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Public route
@app.get("/")
async def public():
    return {"message": "Welcome to the FastAPI App"}

# Login route to redirect the user to Microsoft's login page
@app.get("/login")
async def login():
    client_id = os.getenv("CLIENT_ID")
    redirect_uri = os.getenv("REDIRECT_URI")
    tenant_id = os.getenv("TENANT_ID")
    scopes = os.getenv("SCOPES", "https://graph.microsoft.com/.default")
    auth_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
        f"?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}"
        f"&response_mode=query&scope={scopes}&state=random_state_value"
    )
    logger.info(f"Redirecting user to: {auth_url}")
    return RedirectResponse(auth_url)

# Callback route to handle the authorization code and exchange it for an access token
@app.get("/callback")
async def callback(request: Request):
    try:
        # Extract the authorization code from the query parameters
        params = request.query_params
        authorization_code = params.get("code")
        if not authorization_code:
            return JSONResponse({"error": "Missing authorization code"}, status_code=400)

        # Exchange the authorization code for an access token
        token_url = f"https://login.microsoftonline.com/{os.getenv('TENANT_ID')}/oauth2/v2.0/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "code": authorization_code,
            "redirect_uri": os.getenv("REDIRECT_URI"),
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_response = requests.post(token_url, data=data, headers=headers)
        token_data = token_response.json()

        if "access_token" in token_data:
            logger.info("Access token received successfully.")
            return {"access_token": token_data["access_token"]}
        else:
            logger.error(f"Token exchange failed: {token_data}")
            return JSONResponse({"error": token_data}, status_code=400)
    except Exception as e:
        logger.exception("Error handling callback")
        return JSONResponse({"error": str(e)}, status_code=500)

# Test route to verify authentication
@app.get("/secure-data")
async def secure_data():
    return {"message": "This is protected data!"}

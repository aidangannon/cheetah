import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from src.crosscutting import get_service, Logger, auto_slots
from src.infrastructure import Settings

# Cache JWKS keys from Cognito
jwks = None

def get_public_key(token, jwks):
    headers = jwt.get_unverified_header(token)
    kid = headers["kid"]
    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if key is None:
        raise HTTPException(status_code=401, detail="Invalid token key")
    return key

@auto_slots
class CognitoAuthenticator:

    def __init__(self,
        settings: Settings,
        logger: Logger
    ):
        self.logger = logger
        self.settings = settings

    async def __call__(self, credentials: HTTPAuthorizationCredentials) -> dict:
        global jwks
        if jwks is None:
            keys_url = f"https://cognito-idp.{self.settings.AWS_REGION}.amazonaws.com/{self.settings.USER_POOL_ID}/.well-known/jwks.json"
            jwks = requests.get(keys_url).json()
        token = credentials.credentials
        try:
            key = get_public_key(token, jwks=jwks)
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                issuer=f"https://cognito-idp.{self.settings.AWS_REGION}.amazonaws.com/{self.settings.USER_POOL_ID}",
                audience=self.settings.USER_POOL_CLIENT_ID
            )
            auth_id = payload['sub']
            self.logger.info(f"Token validated", auth_id=auth_id)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
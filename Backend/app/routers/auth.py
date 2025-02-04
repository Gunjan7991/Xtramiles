from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from ..logging_config import logger

from ..database import SessionDep
from ..utils import authenticate_and_generate_token
from ..model import user, store, Token



router = APIRouter(prefix="/api/v1", tags=["Authentication"])
# Configure Limiter
limiter = Limiter(key_func=get_remote_address)

# Define exception
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

@router.post(
    "/login", status_code=status.HTTP_202_ACCEPTED, response_model=Token
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    session:SessionDep,
    login_cred: OAuth2PasswordRequestForm = Depends(),
):
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent", "Unknown")
    try:
        access_token = authenticate_and_generate_token(session, user, login_cred.username, login_cred.password)
        logger.info(f"User {login_cred.username} logged in successfully from {ip_address} - {user_agent}")
        return Token(access_token=access_token, token_type="Bearer")
    except Exception as e:
        logger.warning(f"Failed login attempt for {login_cred.username} from {ip_address} - {user_agent}")
        raise  credentials_exception

@router.post(
    "/storelogin", status_code=status.HTTP_202_ACCEPTED, response_model=Token
)
@limiter.limit("10/minute")
async def store_login(
    request: Request,
    session:SessionDep,
    login_cred: OAuth2PasswordRequestForm = Depends(),
):
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent", "Unknown")
    try:
        access_token = authenticate_and_generate_token(session, store, login_cred.username, login_cred.password)
        logger.info(f"User {login_cred.username} logged in successfully from {ip_address} - {user_agent}")
        return Token(access_token=access_token, token_type="Bearer")
    except Exception as e:
        logger.warning(f"Failed login attempt for {login_cred.username} from {ip_address} - {user_agent}")
        raise  credentials_exception



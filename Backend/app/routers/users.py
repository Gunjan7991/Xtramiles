from sqlmodel import select
from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Annotated
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import logging

from ..model import user, user_create, user_view, user_update_password, user_update_info,user_view_detail
from ..database import SessionDep
from ..utils import hash, verify_password
from ..oauth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/user", tags=["USER"])
# Configure Limiter
limiter = Limiter(key_func=get_remote_address)
# Configure logging
logging.basicConfig(level=logging.INFO)

@router.post("",response_model=user_view, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def create_user(request: Request, new_user: user_create, session: SessionDep):
    user1:user = user(**new_user.model_dump())
    statement = select(user).where(user.email == user1.email)
    user_exists: user = session.exec(statement).first()
    if user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email Already Exists!!")
    statement = select(user).where(user.phone_number == user1.phone_number)
    user_exists: user = session.exec(statement).first()
    if user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Phone Already Exists!!")
    user1.password = hash(user1.password)
    try:
        session.add(user1)
        session.commit()
        session.refresh(user1)
    except Exception as e:
        session.rollback()  # Rollback transaction on failure
        logger.error(f"Purchase update failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request not completed!")
    return user1

@router.get("",  response_model=user_view,  status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
def get_current_user(request: Request, current_user: Annotated[user, Depends(get_current_user)]):
    return current_user

@router.get("/detail",  response_model=user_view_detail,  status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def get_current_user(request: Request, current_user: Annotated[user, Depends(get_current_user)]):
    return current_user

@router.put("/update/password")
@limiter.limit("3/minute")
def update_password(request: Request, update: user_update_password, session:SessionDep,  current_user:Annotated[user, Depends(get_current_user)]):
    if not verify_password(update.current_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password didn't match!")
    current_user.password = hash(update.new_password)
    try:
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
    except e as Exception:
        session.rollback()  # Rollback transaction on failure
        logger.error(f"Purchase update failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request not completed!")
    raise HTTPException(status_code=status.HTTP_201_CREATED,  detail="Password Change Sucessfull")

@router.put("/update/info")
@limiter.limit("3/minute")
def update_address(request: Request, update: user_update_info, session:SessionDep,  current_user:Annotated[user, Depends(get_current_user)]):
    if not verify_password(update.password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password didn't match!")
    if update.address:
        current_user.address = update.address
    if update.phone_number:
        update.phone_number = update.phone_number.replace("-","")
        current_user.phone_number = update.phone_number

    try:
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
    except Exception as e:
        session.rollback()  # Rollback transaction on failure
        logger.error(f"Purchase update failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request not completed!")
    raise HTTPException(status_code=status.HTTP_201_CREATED,  detail="Info Changed Sucessfully")


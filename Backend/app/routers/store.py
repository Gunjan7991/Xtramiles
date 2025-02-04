from sqlmodel import select
from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Annotated
import uuid
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address


from ..model import store, store_create, store_view, store_fuel_update, store_update, user_view, user_by_store,user
from ..database import SessionDep
from ..utils import hash, verify_password
from ..oauth import get_current_store
from ..logging_config import logger


router = APIRouter(prefix="/api/v1/store", tags=["STORE"])
# Configure Limiter
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=store_view, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def create_store(request: Request, new_store: store_create, session: SessionDep):
    logger.info(f"Request from {request.headers.get('X-Forwarded-For', request.client.host)}, User-Agent: {request.headers.get('User-Agent', 'Unknown User-Agent')}")
    store1: store = store(**new_store.model_dump())
    statement = select(store).where(store.email == store1.email)
    store_exists: store = session.exec(statement).first()
    if store_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email Already Exists!!"
        )
    store1.password = hash(store1.password)
    try:
        session.add(store1)
        session.commit()
        session.refresh(store1)
    except Exception as e:
        session.rollback()  # Rollback transaction on failure
        logger.error(f"Purchase update failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request not completed!")
    return store1

@router.get("", response_model=store_view, status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
def get_store(request: Request, current_store: Annotated[store, Depends(get_current_store)]):
    return current_store

@router.get("/fuel", status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
def get_fuel_price(request: Request, current_store: Annotated[store, Depends(get_current_store)]):
    return current_store.fuel_price

@router.put("/fuel", status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def update_fuel_price(
    request: Request, 
    fuel: store_fuel_update,
    session: SessionDep,
    current_store: Annotated[store, Depends(get_current_store)],
):
    current_store.fuel_price = fuel.fuel_price
    try:
        session.add(current_store)
        session.commit()
        session.refresh(current_store)
    except Exception as e:
        session.rollback()  # Rollback transaction on failure
        logger.error(f"Purchase update failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request not completed!")
    return current_store.fuel_price

@router.put("/update/password", status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def update_password(
    request: Request, 
    update: store_update,
    session: SessionDep,
    current_store: Annotated[store, Depends(get_current_store)],
):
    if not verify_password(update.password, current_store.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong Password"
        )
    current_store.password = hash(update.new_password)
    try:
        session.add(current_store)
        session.commit()
        session.refresh(current_store)
    except Exception as e:
        session.rollback()  # Rollback transaction on failure
        logger.error(f"Purchase update failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request not completed!")
    raise HTTPException(status_code=status.HTTP_201_CREATED,  detail="Password Change Sucessfull")

@router.get("/user",  response_model=user_view,  status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def get_customer(request: Request, temp_user: user_by_store, session:SessionDep,  current_store:Annotated[store, Depends(get_current_store)]):
    user_statement = select (user).where(user.user_id==temp_user.user_id)
    current_user: user = session.exec(user_statement).one()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Not Found!")
    return current_user

from sqlmodel import select
from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Annotated
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import logging

from ..oauth import get_current_store, get_current_user
from ..database import SessionDep
from ..model import purchase_create, store, purchase, user, purchase_view, purchases_list, purchase_update
from ..utils import update_purchase_detail

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/purchase", tags=["PURCHASE"])
# Configure Limiter
limiter = Limiter(key_func=get_remote_address)
# Configure logging
logging.basicConfig(level=logging.INFO)

@router.get("", response_model=list[purchases_list], status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
def get_purchase(request: Request, session: SessionDep, current_user: Annotated[user, Depends(get_current_user)],offset: int = 0):
    get_purchase = select(purchase).where(purchase.userId == current_user.user_id).offset(offset*10).limit(10)
    purchases = session.exec(get_purchase).fetchall()
    return purchases

@router.get("/store", response_model=list[purchases_list], status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
def get_purchase(request: Request, session: SessionDep, current_store: Annotated[store, Depends(get_current_store)],offset: int = 0):
    get_purchase = select(purchase).where(purchase.storeId == current_store.store_id).offset(offset*10).limit(10)
    purchases = session.exec(get_purchase).fetchall()
    return purchases

@router.post("", response_model=purchase_view, status_code= status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def create_purchase(request: Request, new_purchase: purchase_create, session: SessionDep, current_store: Annotated[store, Depends(get_current_store)]):
    current_purchase:purchase = purchase(**new_purchase.model_dump())
    user_search = select(user).where(user.user_id == new_purchase.userId)
    current_user:user = session.exec(user_search).first()
    updated_value = update_purchase_detail(False, current_purchase, current_user, current_store)
    try:
        session.add(updated_value[0])
        session.add(updated_value[1])
        session.commit()
        session.refresh(current_purchase)
    except Exception as e:
        session.rollback()  # Rollback transaction on failure
        logger.error(f"Purchase update failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request not completed!")
    return current_purchase

@router.put("/update", response_model=purchase_view, status_code= status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def update_purchase(request: Request, updated_purchase:purchase_update, session: SessionDep, current_store: Annotated[store, Depends(get_current_store)]):
    current_purchase:purchase = session.exec(select(purchase).where(purchase.purchase_id == updated_purchase.purchase_id)).first()
    current_purchase.gallons = updated_purchase.gallons
    current_purchase.grocery  = updated_purchase.grocery
    user_search = select(user).where(user.user_id == current_purchase.userId)
    current_user:user = session.exec(user_search).first()
    updated_value = update_purchase_detail(True, current_purchase, current_user, current_store)
    try:
        session.add(updated_value[0])
        session.add(updated_value[1])
        session.commit()
        session.refresh(current_purchase)
    except Exception as e:
        session.rollback()  # Rollback transaction on failure
        logger.error(f"Purchase update failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request not completed!")
    return current_purchase
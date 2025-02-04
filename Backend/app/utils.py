from passlib.context import CryptContext
from sqlmodel import select

from .model import user, store, purchase, Token
import math
from .oauth import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def calculate_points(gallon: float|None, grocery:float|None)-> int:
    point:int = 0
    if not gallon and not grocery:
        return point
    if gallon:
        if gallon - float(math.floor(gallon)) >= 0.5:
            gallon = math.ceil(gallon)
            
        else:
            gallon = math.floor(gallon)
        point += 2*gallon
    if grocery:
        if grocery - float(math.floor(grocery)) >= 0.5:
            grocery = math.ceil(grocery)
        else:
            grocery = math.floor(grocery)
        point += grocery
    return int(point)

def update_purchase_detail(update: bool, current_purchase: purchase,  current_user:user, current_store:store)->(purchase,user):   
    if current_purchase.gallons >= 75 and update == False:
        current_purchase.is_shower_awarded = True
        current_user.showers = current_user.showers+1
        current_purchase.points_awarded = calculate_points(current_purchase.gallons, current_purchase.grocery)
        current_user.points = current_user.points + current_purchase.points_awarded
        current_purchase.fuel_price = current_store.fuel_price
        current_purchase.storeId = current_store.store_id
        current_purchase.store_name = current_store.store_name
      
    elif current_purchase.gallons >= 75 and update == True:
        temp_point = current_purchase.points_awarded 
        current_purchase.points_awarded = calculate_points(current_purchase.gallons, current_purchase.grocery)
        current_user.points = current_user.points + current_purchase.points_awarded-temp_point
        if not current_purchase.is_shower_awarded:
            current_purchase.is_shower_awarded = True
            current_user.showers = current_user.showers+1


    elif current_purchase.gallons <75  and  update == False:
        current_purchase.points_awarded = calculate_points(current_purchase.gallons, current_purchase.grocery)
        current_user.points = current_user.points + current_purchase.points_awarded
        current_purchase.fuel_price = current_store.fuel_price
        current_purchase.storeId = current_store.store_id
        current_purchase.store_name = current_store.store_name

    else:
        if current_purchase.is_shower_awarded:
            current_purchase.is_shower_awarded = False
            current_user.showers = current_user.showers-1
        temp_point = current_purchase.points_awarded 
        current_purchase.points_awarded = calculate_points(current_purchase.gallons, current_purchase.grocery)
        current_user.points = current_user.points + current_purchase.points_awarded-temp_point
        
    current_purchase.total = current_purchase.fuel_price * current_purchase.gallons + current_purchase.grocery
    return (current_purchase, current_user)


def authenticate_and_generate_token(session, model, username, password):
    statement = select(model).where(model.email == username)
    entity = session.exec(statement).first()

    if not entity or not verify_password(password, entity.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )
    if model == user:
        return create_access_token(
            data={"id": str(entity.user_id), "name": str(entity.name)}
        )
    else:
        return create_access_token(
            data={"id": str(entity.store_id), "name": str(entity.name)}
        )
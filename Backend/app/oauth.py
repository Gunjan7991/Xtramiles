import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from typing import Annotated

from . import model
from .database import SessionDep
from .config import SECRET_KEY,ALGORITHM,EXP_TIME



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

secret_key=SECRET_KEY
algorithm=ALGORITHM
exp_time = EXP_TIME
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=exp_time
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token=token, key=secret_key, algorithms=algorithm
        )
        usr_id: str = payload.get("user_id")
        usr_name: str = payload.get("name")

        if usr_id is None:
            raise credentials_exceptions

        token_data = model.TokenData(id=str(usr_id), name=usr_name)

    except Exception as e:
        raise credentials_exceptions

    return token_data


async def get_current_user(session:SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        t_id: str = payload.get("user_id")
        t_name: str = payload.get("name")
        if t_id is None:
            raise credentials_exception
        
        token_data = model.TokenData(id=t_id, name=t_name)
    except InvalidTokenError:
        raise credentials_exception
    statement = select(model.user).where(model.user.user_id == t_id)
    user1: model.user = session.exec(statement).first()
    if user1 is None:
        raise credentials_exception
    return user1

async def get_current_store(session:SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        t_id: str = payload.get("id")
        t_name: str = payload.get("name")
        if t_id is None:
            raise credentials_exception
        
        token_data = model.TokenData(id=t_id, name=t_name)
    except InvalidTokenError:
        raise credentials_exception
    statement = select(model.store).where(model.store.store_id == t_id)
    store1: model.store = session.exec(statement).first()
    if store1 is None:
        raise credentials_exception
    return store1

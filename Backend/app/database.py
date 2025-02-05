from sqlmodel import  create_engine, SQLModel, Session
from typing import Annotated
from fastapi import Depends

from .config import DATABASE_URL
from .logging_config import logger

engine = create_engine(DATABASE_URL)


def init_db():
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("DATABASE INITIALIZED SUCESSFULLY.")
    except Exception as e:
        logger.fatal(f"Failed to initialize database!{e}")


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

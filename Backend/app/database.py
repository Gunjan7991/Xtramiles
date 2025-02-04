from sqlmodel import  create_engine, SQLModel, Session
from typing import Annotated
from fastapi import Depends

# SQL LITE
# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"
# SQLALCHEMY_DATABASE_URL = sqlite_url

# PostgreSQL
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:apple@localhost:5432/xtraMiles"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo = False)


def init_db():
    try:
        SQLModel.metadata.create_all(engine)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

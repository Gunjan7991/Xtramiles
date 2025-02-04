import uuid
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from pydantic import EmailStr
"""
USERS
"""
class user_base(SQLModel):
    name:str = Field (nullable=False, max_length=99)
    email: EmailStr = Field(nullable=False, unique= True, max_length=99)
    phone_number:str = Field(nullable=False, unique=True, max_length=10)
    address:str = Field(nullable=False)
    password:str = Field(nullable=False, min_length=8, max_length=99)

class user(user_base, table=True):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    points: float = Field(default=0.0)
    showers: int = Field(default=0)
    verified:bool = Field(default=False)

class user_create(user_base):
    pass

class user_view(SQLModel):
    name:str
    points: float 
    showers: int 

class user_view_detail(user_view):
    address:str
    phone_number:str
    email:EmailStr
    user_id: uuid.UUID

class user_by_store(SQLModel):
    user_id: uuid.UUID

class user_update(SQLModel):
    password: str = Field(nullable=False)
    email: EmailStr = None 
    phone_number: Optional[str] = None
    address: Optional[str] = None

class user_update_password(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

class user_update_info(SQLModel):
    address: str | None
    phone_number: str | None
    password: str
"""
Store
"""
class store_base(SQLModel):
    store_name:str = Field(nullable=False)
    email:EmailStr = Field(nullable=False)
    password:str = Field(nullable=False)
    address:str = Field(nullable=False)
    

class store(store_base, table = True):
    store_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fuel_price: float= Field(nullable=False, default=0.0)

class store_create(store_base):
    pass

class store_view(SQLModel):
    store_id: uuid.UUID
    store_name:str
    fuel_price: float

class store_update(SQLModel):
    password: str
    new_password: str

class store_fuel_update(SQLModel):
    fuel_price: float
"""
Purchase
"""
class purchase_base(SQLModel):
    gallons:float|None 
    grocery:float|None

class purchase(purchase_base, table=True):
    fuel_price:float
    is_shower_awarded: bool = Field(default=False)
    points_awarded:float
    store_name: str
    total: float
    purchase_id:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    userId: uuid.UUID = Field(foreign_key="user.user_id", nullable=False, ondelete="CASCADE")
    storeId: uuid.UUID = Field(foreign_key="store.store_id", nullable=False, ondelete="CASCADE")
    updated_at: datetime | None = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    
class purchase_create(purchase_base):
    userId: uuid.UUID

class purchase_view(SQLModel):
    purchase_id:uuid.UUID
    points_awarded: float
    is_shower_awarded: bool

class purchases_list(purchase_view):
    total: float|None
    store_name: str|None

class purchase_update(SQLModel):
    purchase_id:uuid.UUID
    gallons:float|None 
    grocery:float|None
    
"""
Token
"""
class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    id: str | None 
    name: str | None
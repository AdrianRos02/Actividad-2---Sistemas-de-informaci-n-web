from datetime import datetime, timedelta, timezone
from typing import Annotated

from models import Producto,Cliente,Pedido
from services import (update_product_service,get_product_service,get_all_products_service,delete_product_service,register_client_service, create_order_service, generate_sales_report_service,)
from typing import Union


import jwt
from fastapi import Depends,FastAPI,HTTPException,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

#TODO: estos valoes deberian esta en variables de entorno
SECRET_KEY = "604f4b0bb91cbf5d981f3152a0b2223eceaf22f18df22d1e7511a835da818a20"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES =30

fake_users_db = {
    "adrian":{
        "username": "adrian",
        "full_name": "adrian rosello",
        "email": "adrian@ejemplo.com",
        "hashed_password": "$2b$12$6yf51PFwhNs7XckNaTVu6uBnbw4MYImGDpP/VNyOmaY.uq1VltS7S",
        "disabled":False,
    },
}
class Token(BaseModel):
    access_token: str
    token_type:str

class TokenData(BaseModel):
    username: str | None=None

#Modelos basicos de ususarios para BD
class User(BaseModel):
    username: str
    email:str | None=None
    full_name:str | None=None
    disabled:bool | None=None

class UserInDB(User):
    hashed_password:str

#Esquema de autenticacion
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme= OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

#usuarios
def get_user(db,username:str):
    if username in db:
        user_dict =db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db,username: str, password: str):
    user=get_user(fake_db,username)
    if not user:
        return False
    if not verify_password(password,user.hashed_password):
        return False
    return user

#passwords
def get_password_hash(password):
     return pwd_context.hash(password)

def verify_password(plain_password,hashed_password):
     return pwd_context.verify(plain_password,hashed_password)
    
#Token
def create_access_token(data: dict, expires_delta:timedelta |None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token:Annotated[str,Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user= get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
        current_user:Annotated[User,Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400,detail="Inactive user")
    return current_user

#Rutas
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
 )->Token:
    user = authenticate_user(fake_users_db,form_data.username,form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username o password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return{"access_token": access_token, "token_type":"bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User,Depends(get_current_active_user)]):
    return current_user

#CRUD DE PRODUCTOS
@app.get("/products/{product_id}")
def read_product(product_id: int, query: Union[str, None]= None):
    product = get_product_service(product_id)
    if product:
        return product
    else:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.put("/products/{product_id}")
def update_product(product_id: int, product: Producto):
    return update_product_service(product_id,product)

@app.get("/products/")
def read_all_products():
    return get_all_products_service()

@app.delete("/products/{product_id}")
def delete_product(product_id:int):
    return delete_product_service(product_id)

@app.post("/clients/")
def register_client(cliente: Cliente):
    return register_client_service(cliente)


@app.post("/orders/")
def create_order(order: Pedido):
    return create_order_service(order)

@app.get("/sales-report/")
def sales_report():
    return generate_sales_report_service()

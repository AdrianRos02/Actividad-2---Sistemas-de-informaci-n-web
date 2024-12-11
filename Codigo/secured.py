from datetime import datetime, timedelta, timezone
from typing import Annotated

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
        "hashed_password": "$2b$12$cMWVCqJlS/yEqcFk6eUiAuTcMNQkzsI1Q/t/VEPhMkZ.HNmmJIE1G",
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

@app.post("/generate-hash")
async def generate_hash(password: str):
    hashed_password = get_password_hash(password)
    return {"password": password, "hashed_password": hashed_password}
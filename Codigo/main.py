from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel

fake_users_db = {
    "adrian":{
        "username": "adrian",
        "full_name": "adrian rosello",
        "email": "adrian@ejemplo.com",
        "hashed_password": "fakehashedsecret",
        "disabled":False,
    },
     "Usuario":{
        "username": "Usuario",
        "full_name": "Usuario prueba",
        "email": "usuario@ejemplo.com",
        "hashed_password": "fakehashedsecret2",
        "disabled":True,
    }
}

app= FastAPI()

def fake_hash_password(password:str):
    return "fakehashed" + password

#Modelo de autenticacion
#Esquema de autenticacion a utulizar
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#Modelos basicos de ususarios para BD
class User(BaseModel):
    username: str
    email:str | None=None
    full_name:str | None=None
    disabled:bool | None=None

class UserInDB(User):
    hashed_password:str

def get_user(db,username:str):
    if username in db:
        user_dict =db[username]
        return UserInDB(**user_dict)
    
def fake_decode_token(token):
    user = get_user(fake_users_db,token)
    return user

async def get_current_user(token:Annotated[str,Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
        current_user:Annotated[User,Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400,detail="Inactive user")
    return current_user

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    #exista el usuario
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username o password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user =UserInDB(**user_dict)
    #que la clave esta bien
    hashed_password= fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username o password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return{"access_token": user.username, "token_type":"bearer"}


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User,Depends(get_current_active_user)]):
    return current_user

@app.get("/products/")
async def read_products(current_user: Annotated[User,Depends(get_current_active_user)]):
    return{"user": current_user.username}
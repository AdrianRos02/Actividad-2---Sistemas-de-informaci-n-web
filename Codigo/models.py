from pydantic import BaseModel
from typing import List, Union

class Producto(BaseModel):
    nombre: str
    descripcion: str
    precio:float 
    categoria: str
    stock: str

class Cliente(BaseModel):
    nombre: str
    correo: str

class Pedido(BaseModel):
    cliente_id: int
    productos: List[int]  # IDs de los productos
    total: float

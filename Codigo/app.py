from fastapi import FastAPI, HTTPException
from models import Producto,Cliente,Pedido
from services import (update_product_service,get_product_service,get_all_products_service,delete_product_service,register_client_service, create_order_service, generate_sales_report_service,)
from typing import Union

app = FastAPI()

@app.get("/")
def index():
    return {"message": "Hello, World!"}

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
from models import Producto,Cliente,Pedido
from dao import insert_or_update_product, get_product,get_all_products,delete_products,insert_client, insert_order,get_sales_report

def update_product_service(product_id: int, product: Producto):
    #Se puede agregar logica de control de esta operacion
    insert_or_update_product(product_id, product)
    return {"product_id": product_id,
            "nombre": product.nombre,
            "descripcion": product.descripcion,
            "precio": product.precio,
            "categoria": product.categoria,
            "stock": product.stock
            }
def get_product_service(product_id: int):
    producto = get_product(product_id)
    if producto:
        return {"product_id": product_id,
                "nombre": producto[0],
                "descripcion": producto[1],
                "precio": producto[2],
                "categoria": producto[3],
                "stock": producto[4]}
    else:
        return None

def get_all_products_service():
    productos = get_all_products()
    productos_list = []
    for producto in productos:
        productos_list.append({"product_id": producto[0],
                "nombre": producto[1],
                "descripcion": producto[2],
                "precio": producto[3],
                "categoria": producto[4],
                "stock": producto[5]})
    return productos_list

def delete_product_service(product_id: int):
    delete_products(product_id)
    return{"message": f"Producto ID={product_id} eliminado exitosamente" }

def register_client_service(cliente: Cliente):
    insert_client(cliente)
    return {"message": f"Cliente {cliente.nombre} registrado con éxito."}

def create_order_service(order):
    insert_order(order)
    return {"message": "Pedido creado exitosamente"}

def generate_sales_report_service():
    report = get_sales_report()
    return {"sales_report": report}
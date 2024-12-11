import sqlite3
from models import Producto,Cliente,Pedido

def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

def create_product_table():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE  IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    precio REAL NOT NULL,
                    categoria TEXT NOT NULL,
                    stock TEXT NOT NULL
                    );
                    ''')

        conn.commit()
        conn.close()

def insert_or_update_product(product_id:int, product: Producto):
      conn = get_db_connection()
      cursor= conn.cursor()

      cursor.execute('''
        INSERT INTO productos (id,nombre ,descripcion ,precio,categoria,stock)
        VALUES(?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
                nombre = excluded.nombre,
                descripcion = excluded.descripcion,
                precio = excluded.precio,
                categoria = excluded.categoria,
                stock = excluded.stock;
      ''', (product_id,product.nombre,product.descripcion,product.precio,product.categoria,product.stock))
    
      conn.commit()
      conn.close()

def get_product(product_id:int):
     conn = get_db_connection()
     cursor = conn.cursor()

     cursor.execute('''
     SELECT nombre, descripcion, precio, categoria, stock FROM productos WHERE id=?;
     ''', (product_id,))
     producto= cursor.fetchone()
     conn.close()
     return producto

def get_all_products():
     conn = get_db_connection()
     cursor = conn.cursor()
     cursor.execute('''
     SELECT id,nombre, descripcion, precio, categoria, stock FROM productos;
     ''')
     productos= cursor.fetchall()
     conn.close()
     return productos

def delete_products(product_id:int):
     conn = get_db_connection()
     cursor = conn.cursor()
     cursor.execute('DELETE FROM productos WHERE id = ?;',(product_id,))
     conn.commit()
     conn.close()
           
def create_client_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        correo TEXT UNIQUE NOT NULL
    );
    ''')

    conn.commit()
    conn.close()

def create_order_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY,
        cliente_id INTEGER NOT NULL,
        productos TEXT NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    );
    ''')

    conn.commit()
    conn.close()

def insert_client(cliente: Cliente):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO clientes (nombre, correo)
    VALUES (?, ?)
    ''', (cliente.nombre, cliente.correo))

    conn.commit()
    conn.close()

def insert_order(order):
    conn = get_db_connection()
    cursor = conn.cursor()

    productos_str = ",".join(map(str, order.productos))

    cursor.execute('''
    INSERT INTO pedidos (cliente_id, productos, total)
    VALUES (?, ?, ?)
    ''', (order.cliente_id, productos_str, order.total))

    conn.commit()
    conn.close()

def get_sales_report():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT clientes.nombre, pedidos.total
    FROM pedidos
    INNER JOIN clientes ON pedidos.cliente_id = clientes.id
    ''')

    report = cursor.fetchall()
    conn.close()
    return report
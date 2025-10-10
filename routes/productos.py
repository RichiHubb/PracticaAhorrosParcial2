from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection
from pusher_utils import trigger_pusher

productos_bp = Blueprint('productos', __name__)

@productos_bp.route("/productos")
def productos():
    # Used as Angular templateUrl; always return the fragment so the
    # client receives the correct partial. If you need direct navigation
    # to return the full shell, create a separate route for that.
    return render_template("productos.html")

@productos_bp.route("/tbodyProductos")
def tbodyProductos():
    with get_db_connection() as con:
        cursor = con.cursor(dictionary=True)
        sql = """
        SELECT Id_Producto, Nombre_Producto, Precio, Existencias
        FROM productos
        ORDER BY Id_Producto DESC
        LIMIT 10 OFFSET 0
        """
        cursor.execute(sql)
        registros = cursor.fetchall()
    return render_template("tbodyProductos.html", productos=registros)

@productos_bp.route("/productos/ingredientes/<int:id>")
def productosIngredientes(id):
    with get_db_connection() as con:
        cursor = con.cursor(dictionary=True)
        sql = """
        SELECT productos.Nombre_Producto, ingredientes.*, productos_ingredientes.Cantidad
        FROM productos_ingredientes
        INNER JOIN productos ON productos.Id_Producto = productos_ingredientes.Id_Producto
        INNER JOIN ingredientes ON ingredientes.Id_Ingrediente = productos_ingredientes.Id_Ingrediente
        WHERE productos_ingredientes.Id_Producto = %s
        ORDER BY productos.Nombre_Producto
        """
        cursor.execute(sql, (id,))
        registros = cursor.fetchall()
    return render_template("modal.html", productosIngredientes=registros)

@productos_bp.route("/productos/buscar", methods=["GET"])
def buscarProductos():
    busqueda = f"%{request.args.get('busqueda', '')}%"
    with get_db_connection() as con:
        cursor = con.cursor(dictionary=True)
        sql = """
        SELECT Id_Producto, Nombre_Producto, Precio, Existencias
        FROM productos
        WHERE Nombre_Producto LIKE %s OR Precio LIKE %s OR Existencias LIKE %s
        ORDER BY Id_Producto DESC
        LIMIT 10 OFFSET 0
        """
        cursor.execute(sql, (busqueda, busqueda, busqueda))
        registros = cursor.fetchall()
    return jsonify(registros)

@productos_bp.route("/producto", methods=["POST"])
def guardarProducto():
    id = request.form.get("id")
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    existencias = request.form.get("existencias")
    with get_db_connection() as con:
        cursor = con.cursor()
        if id:
            sql = """
            UPDATE productos SET Nombre_Producto = %s, Precio = %s, Existencias = %s WHERE Id_Producto = %s
            """
            cursor.execute(sql, (nombre, precio, existencias, id))
        else:
            sql = """
            INSERT INTO productos (Nombre_Producto, Precio, Existencias) VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (nombre, precio, existencias))
        con.commit()
    trigger_pusher("canalProductos", "eventoProductos", "Producto actualizado")
    return jsonify({})

@productos_bp.route("/producto/<int:id>")
def editarProducto(id):
    with get_db_connection() as con:
        cursor = con.cursor(dictionary=True)
        sql = "SELECT Id_Producto, Nombre_Producto, Precio, Existencias FROM productos WHERE Id_Producto = %s"
        cursor.execute(sql, (id,))
        registros = cursor.fetchall()
    return jsonify(registros)

@productos_bp.route("/producto/eliminar", methods=["POST"])
def eliminarProducto():
    id = request.form.get("id")
    with get_db_connection() as con:
        cursor = con.cursor()
        sql = "DELETE FROM productos WHERE Id_Producto = %s"
        cursor.execute(sql, (id,))
        con.commit()
    return jsonify({})

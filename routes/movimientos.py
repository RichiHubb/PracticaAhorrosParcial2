from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection
from pusher_utils import trigger_pusher

movimientos_bp = Blueprint('movimientos', __name__)

@movimientos_bp.route("/movimientos")
def viewMovimientos():
    return render_template("movimientos.html")

@movimientos_bp.route("/tbodyMovimientos")
def tbodyMovimientos():
    import datetime
    import pytz
    with get_db_connection() as con:
        cursor = con.cursor(dictionary=True)
        sql = """
        SELECT idMovimiento, monto, fechaHora
        FROM movimientos
        ORDER BY fechaHora DESC
        """
        cursor.execute(sql)
        registros = cursor.fetchall()
        for registro in registros:
            fecha_hora = registro["fechaHora"]
            if fecha_hora:
                registro["fechaHora"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
            else:
                registro["fechaHora"] = ""
    return render_template("tbodyMovimientos.html", movimientos=registros)

@movimientos_bp.route("/movimiento", methods=["POST"])
def guardarMovimiento():
    import datetime
    import pytz
    monto = request.form.get("monto")
    fechaHora = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    with get_db_connection() as con:
        cursor = con.cursor()
        sql = "INSERT INTO movimientos (monto, fechaHora) VALUES (%s, %s)"
        cursor.execute(sql, (monto, fechaHora))
        con.commit()
    trigger_pusher("canalMovimientos", "eventoMovimientos", "Movimiento actualizado")
    return jsonify({})

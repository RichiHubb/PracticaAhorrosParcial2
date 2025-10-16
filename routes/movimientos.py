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
        SELECT idMovimiento, fechaHora, concepto, monto
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

    idMovimiento = request.form.get("idMovimiento")
    fecha = request.form.get("fecha")   
    concepto = request.form.get("concepto")
    monto = request.form.get("monto")

    if not fecha or fecha.strip() == "":
        fechaHora = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    else:
        try:
            fechaHora = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
        except:
            fechaHora = datetime.datetime.now(pytz.timezone("America/Matamoros"))

    with get_db_connection() as con:
        cursor = con.cursor()

        if idMovimiento and idMovimiento.strip() != "":
            sql = """
            UPDATE movimientos
            SET fechaHora = %s, concepto = %s, monto = %s
            WHERE idMovimiento = %s
            """
            cursor.execute(sql, (fechaHora, concepto, monto, idMovimiento))
        else:
            sql = "INSERT INTO movimientos (fechaHora, concepto, monto) VALUES (%s, %s, %s)"
            cursor.execute(sql, (fechaHora, concepto, monto))

        con.commit()

    trigger_pusher("canalMovimientos", "eventoMovimientos", "Movimiento actualizado")

    return jsonify({"status": "ok"})

@movimientos_bp.route("/eliminarMovimiento", methods=["POST"])
def eliminarMovimiento():
    idMovimiento = request.form.get("idMovimiento")

    if not idMovimiento:
        return jsonify({"status": "error", "message": "Falta ID"}), 400

    with get_db_connection() as con:
        cursor = con.cursor()
        sql = "DELETE FROM movimientos WHERE idMovimiento = %s"
        cursor.execute(sql, (idMovimiento,))
        con.commit()

    trigger_pusher("canalMovimientos", "eventoMovimientos", "Movimiento eliminado")

    return jsonify({"status": "eliminado"})

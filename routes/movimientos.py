from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection
from pusher_utils import trigger_pusher
import datetime
import pytz

movimientos_bp = Blueprint('movimientos', __name__)

@movimientos_bp.route("/movimientos")
def viewMovimientos():
    return render_template("movimientos.html")


@movimientos_bp.route("/tbodyMovimientos")
def tbodyMovimientos():
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
    idMovimiento = request.form.get("idMovimiento")
    monto = request.form.get("monto")

    fechaHora = datetime.datetime.now(pytz.timezone("America/Matamoros"))

    with get_db_connection() as con:
        cursor = con.cursor()

        if idMovimiento and idMovimiento.strip() != "":
            sql = """
            UPDATE movimientos
            SET monto = %s, fechaHora = %s
            WHERE idMovimiento = %s
            """
            cursor.execute(sql, (monto, fechaHora, idMovimiento))
        else:
            sql = "INSERT INTO movimientos (monto, fechaHora) VALUES (%s, %s)"
            cursor.execute(sql, (monto, fechaHora))

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

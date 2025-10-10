from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection
from pusher_utils import trigger_pusher

movimientos_etiquetas_bp = Blueprint('movimientosEtiquetas', __name__)

@movimientos_etiquetas_bp.route("/movimientosEtiquetas")
def viewmovimientosEtiquetas():
    return render_template("movimientosetiquetas.html")

@movimientos_etiquetas_bp.route("/tbodyMovimientosEtiquetas")
def tbodyMovimientosetiquetas():
    with get_db_connection() as con:
        cursor = con.cursor(dictionary=True)
        sql = """
        SELECT idMovimientoEtiqueta, idMovimiento, idEtiqueta
        FROM movimientosetiquetas
        ORDER BY idMovimientoEtiqueta DESC
        LIMIT 10 OFFSET 0
        """
        cursor.execute(sql)
        registros = cursor.fetchall()
    return render_template("tbodyMovimientosEtiquetas.html", movimientosetiquetas=registros)


@movimientos_etiquetas_bp.route("/movimientoetiqueta", methods=["POST"])
def guardarMovimientoEtiqueta():
    idMovimiento = request.form.get("idMovimiento")
    idEtiqueta = request.form.get("idEtiqueta")
    with get_db_connection() as con:
        cursor = con.cursor()
        sql = "INSERT INTO movimientosetiquetas (idMovimiento, idEtiqueta) VALUES (%s, %s)"
        cursor.execute(sql, (idMovimiento, idEtiqueta))
        con.commit()
    trigger_pusher("canalMovimientosEtiquetas", "eventoMovimientosEtiquetas", "Movimiento etiqueta actualizado")
    return jsonify({})
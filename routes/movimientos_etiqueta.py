from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection
from pusher_utils import trigger_pusher

movimientos_etiquetas_bp = Blueprint('movimientosEtiquetas', __name__)

# Página principal
@movimientos_etiquetas_bp.route("/movimientosEtiquetas")
def viewmovimientosEtiquetas():
    return render_template("movimientosetiquetas.html")


# Cargar tabla dinámica (tbody)
@movimientos_etiquetas_bp.route("/tbodyMovimientosEtiquetas")
def tbodyMovimientosetiquetas():
    with get_db_connection() as con:
        cursor = con.cursor(dictionary=True)
        sql = """
        SELECT idMovimientoEtiqueta, idMovimiento, idEtiqueta
        FROM movimientosetiquetas
        ORDER BY idMovimientoEtiqueta DESC
        """
        cursor.execute(sql)
        registros = cursor.fetchall()
    return render_template("tbodyMovimientosEtiquetas.html", movimientosetiquetas=registros)


# Insertar o actualizar registro
@movimientos_etiquetas_bp.route("/movimientoetiqueta", methods=["POST"])
def guardarMovimientoEtiqueta():
    idMovimientoEtiqueta = request.form.get("idMovimientoEtiqueta")
    idMovimiento = request.form.get("idMovimiento")
    idEtiqueta = request.form.get("idEtiqueta")

    with get_db_connection() as con:
        cursor = con.cursor()

        # Si hay un ID válido, actualizamos el registro existente
        if idMovimientoEtiqueta and idMovimientoEtiqueta.strip() != "":
            sql = """
            UPDATE movimientosetiquetas
            SET idMovimiento = %s, idEtiqueta = %s
            WHERE idMovimientoEtiqueta = %s
            """
            cursor.execute(sql, (idMovimiento, idEtiqueta, idMovimientoEtiqueta))
        else:
            # Si no hay ID, insertamos uno nuevo
            sql = "INSERT INTO movimientosetiquetas (idMovimiento, idEtiqueta) VALUES (%s, %s)"
            cursor.execute(sql, (idMovimiento, idEtiqueta))

        con.commit()

    #Notificar al frontend que hubo cambios
    trigger_pusher("canalMovimientosEtiquetas", "eventoMovimientosEtiquetas", "Movimiento etiqueta actualizado")

    return jsonify({"status": "ok"})


# Eliminar registro
@movimientos_etiquetas_bp.route("/eliminarMovimientoEtiqueta", methods=["POST"])
def eliminarMovimientoEtiqueta():
    idMovimientoEtiqueta = request.form.get("idMovimientoEtiqueta")

    if not idMovimientoEtiqueta:
        return jsonify({"status": "error", "message": "Falta ID"}), 400

    with get_db_connection() as con:
        cursor = con.cursor()
        sql = "DELETE FROM movimientosetiquetas WHERE idMovimientoEtiqueta = %s"
        cursor.execute(sql, (idMovimientoEtiqueta,))
        con.commit()

    # Notificar actualización
    trigger_pusher("canalMovimientosEtiquetas", "eventoMovimientosEtiquetas", "Movimiento etiqueta eliminado")

    return jsonify({"status": "eliminado"})


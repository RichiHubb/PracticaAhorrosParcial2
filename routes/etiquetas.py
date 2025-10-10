from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection
from pusher_utils import trigger_pusher

etiquetas_bp = Blueprint('etiquetas', __name__)

@etiquetas_bp.route("/etiquetas")
def viewEtiquetas():
    return render_template("etiquetas.html")

@etiquetas_bp.route("/tbodyEtiquetas")
def tbodyEtiquetas():
    with get_db_connection() as con:
        cursor = con.cursor(dictionary=True)
        sql = """
        SELECT idEtiqueta, nombreEtiqueta
        FROM etiquetas
        ORDER BY idEtiqueta DESC
        """
        cursor.execute(sql)
        registros = cursor.fetchall()
    return render_template("tbodyEtiquetas.html", etiquetas=registros)

@etiquetas_bp.route("/etiqueta", methods=["POST"])
def guardarEtiqueta():
    nombre = request.form.get("nombre")
    with get_db_connection() as con:
        cursor = con.cursor()
        sql = "INSERT INTO etiquetas (nombreEtiqueta) VALUES (%s)"
        cursor.execute(sql, (nombre,))
        con.commit()
    trigger_pusher("canalEtiquetas", "eventoEtiquetas", "Etiqueta actualizada")
    return jsonify({})
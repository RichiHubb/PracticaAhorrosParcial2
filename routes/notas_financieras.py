from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection
from pusher_utils import trigger_pusher

notas_financieras_bp = Blueprint('notas_financieras', __name__)

@notas_financieras_bp.route("/notasFinancieras")
def notasfinancieras():
    return render_template("notasFinancieras.html")

@notas_financieras_bp.route("/tbodyNotasFinancieras")
def tbodyNotasFinancieras():
    with get_db_connection() as con:
        cursor = con.cursor(dictionary=True)
        sql = """
        SELECT idNota, titulo, descripcion, fechaCreacion
        FROM notasfinancieras
        ORDER BY idNota DESC
        LIMIT 10 OFFSET 0
        """
        cursor.execute(sql)
        registros = cursor.fetchall()
        # Si manejas fechas y horas
        for registro in registros:
            fecha_hora = registro["fechaCreacion"]
            if fecha_hora:
                registro["fechaCreacion"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
            else:
                registro["fechaCreacion"] = ""
    return render_template("tbodyNotasFinancieras.html", notas=registros)

@notas_financieras_bp.route("/notafinanciera", methods=["POST"])
def guardarNotaFinanciera():
    titulo = request.form.get("titulo")
    descripcion = request.form.get("descripcion")
    with get_db_connection() as con:
        cursor = con.cursor()
        sql = "INSERT INTO notasfinancieras (titulo, descripcion) VALUES (%s, %s)"
        cursor.execute(sql, (titulo, descripcion))
        con.commit()
    trigger_pusher("canalNotasFinancieras", "eventoNotasFinancieras", "Nota financiera actualizada")
    return jsonify({})

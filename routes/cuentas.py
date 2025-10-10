from flask import Blueprint, render_template, request, jsonify, current_app
from db import get_db_connection
from pusher_utils import trigger_pusher

cuentas_bp = Blueprint('cuentas', __name__)

@cuentas_bp.route("/cuentas")
def viewCuentas():
    return render_template("cuentas.html")

@cuentas_bp.route("/tbodyCuentas")
def tbodyCuentas():
    with get_db_connection() as con:
        cursor = con.cursor(dictionary=True)
        sql = "SELECT id_cuenta, nombre, balance FROM cuentas ORDER BY id_cuenta DESC"
        cursor.execute(sql)
        registros = cursor.fetchall()

    return render_template("tbodyCuentas.html", cuentas=registros)

@cuentas_bp.route("/cuenta", methods=["POST"])
def guardarCuenta():
    nombre = request.form.get("nombre")
    balance = request.form.get("balance")
    with get_db_connection() as con:
        cursor = con.cursor()
        sql = "INSERT INTO cuentas (nombre, balance) VALUES (%s, %s)"
        cursor.execute(sql, (nombre, balance))
        con.commit()
    trigger_pusher("canalCuentas", "eventoCuentas", "Cuenta actualizada")
    return jsonify({})

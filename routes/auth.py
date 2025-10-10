from flask import Blueprint, request, jsonify, render_template, session
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login")
def viewLogin():
    return render_template("login.html")

@auth_bp.route("/iniciarSesion", methods=["POST"])
def iniciarSesion():
    username = request.form.get("username")
    password = request.form.get("password")
    with get_db_connection() as con:
        cursor = con.cursor(dictionary=True)
        sql = "SELECT id FROM usuarios WHERE nombre = %s AND contrasena = %s"
        cursor.execute(sql, (username, password))
        registros = cursor.fetchall()
    if registros and len(registros) > 0:
        session['user_id'] = registros[0]['id']
        return jsonify({'ok': True, 'redirect': '/'})
    return jsonify({'ok': False})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop('user_id', None)
    return jsonify({'ok': True, 'redirect': '/'})


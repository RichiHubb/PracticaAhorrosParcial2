# python.exe -m venv .venv
# cd .venv/Scripts
# activate.bat
# py -m ensurepip --upgrade
# pip install -r requirements.txt

import os
from flask import Flask, render_template, session
from flask_cors import CORS
from config import Config

from routes.auth import auth_bp
from routes.productos import productos_bp
from routes.cuentas import cuentas_bp
from routes.notas_financieras import notas_financieras_bp
from routes.movimientos_etiqueta import movimientos_etiquetas_bp
from routes.etiquetas import etiquetas_bp
from routes.movimientos import movimientos_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# SECRET_KEY is required for session support. Prefer setting SECRET_KEY in
# environment for production. We fall back to a dev key if not set.
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(cuentas_bp)
app.register_blueprint(notas_financieras_bp)
app.register_blueprint(movimientos_etiquetas_bp)
app.register_blueprint(etiquetas_bp)
app.register_blueprint(movimientos_bp)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/top_section.html')
def top_section():
    return render_template('top_section.html')


@app.context_processor
def inject_logged_in():
    # Expose a `logged_in` boolean to all templates
    return { 'logged_in': ('user_id' in session) }

if __name__ == "__main__":
        app.run(debug=True)

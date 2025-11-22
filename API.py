from flask import Flask
from ENDPOINTS.Usuario import usuario_bp


app = Flask(__name__)

# Registrar os blueprints
app.register_blueprint(usuario_bp)


if __name__ == "__main__":
    app.run(debug=True)


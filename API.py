from flask import Flask
from ENDPOINTS.Usuario import usuario_bp
from ENDPOINTS.Paciente import paciente_bp
from ENDPOINTS.ProfissionalSaude import profissionalSaude_bp
from ENDPOINTS.Consulta import consulta_bp
from ENDPOINTS.Teleconsulta import teleconsulta_bp
from ENDPOINTS.Prontuario import prontuario_bp
from ENDPOINTS.Prescricao import prescricao_bp
from ENDPOINTS.Auditoria import auditoria_bp
from ENDPOINTS.AcessoSistema import acessosistema_bp
from ENDPOINTS.Administrador import administrador_bp

app = Flask(__name__)

# Registrar os blueprints
app.register_blueprint(usuario_bp)
app.register_blueprint(paciente_bp)
app.register_blueprint(profissionalSaude_bp)
app.register_blueprint(consulta_bp)
app.register_blueprint(teleconsulta_bp)
app.register_blueprint(prontuario_bp)
app.register_blueprint(prescricao_bp)
app.register_blueprint(auditoria_bp)
app.register_blueprint(acessosistema_bp)
app.register_blueprint(administrador_bp)

if __name__ == "__main__":
    app.run(debug=True)


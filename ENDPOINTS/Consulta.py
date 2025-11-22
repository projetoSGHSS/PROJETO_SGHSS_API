from flask import Blueprint, request, jsonify, abort
from CONECTAR.funcaoConectar import conectar

consulta_bp = Blueprint("Consulta", __name__)

##############################################
#ROTAS PARA A TABELA CONSULTA

##ROTA GET
##############################################
@consulta_bp.route("/Consulta", methods=["GET"])
def listar_Consultas():
    conn = conectar()
    conn.execute("PRAGMA foreign_keys = ON") #ativa as chaves estrangeiras das tabelas (pois, não é ativado por padrão)
    cursor = conn.cursor()
    cursor.execute("SELECT id, dataHora, status, pacienteId, profissionalId  FROM Consulta")
    dados = [
        {"id": row[0], "dataHora": row[1], "status": row[2], "pacienteId": row[3], "profissionalId": row[4] }
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(dados)

##ROTA DELETE
#############################################
from flask import jsonify, abort

@consulta_bp.route("/Consulta/<int:id_consulta>", methods=["DELETE"])
def deletar_consulta(id_consulta):
    conn = conectar()
    cursor = conn.cursor()

    # tenta apagar o registro informado
    cursor.execute("DELETE FROM Consulta WHERE id = ?", (id_consulta,))
    conn.commit()

    # cursor.rowcount informa quantas linhas foram afetadas
    if cursor.rowcount == 0:
        conn.close()
        # nenhum registro com esse ID → devolve 404
        abort(404, description="Consulta não encontrada")

    conn.close()
    # 204 = No Content (padrão para deleções bem‑sucedidas)
    return ("", 204)


##ROTA INSERT
#############################################

from flask import request, jsonify, abort
@consulta_bp.route("/Consulta", methods=["POST"])
def criar_usuario():
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Validação de campos obrigatórios
    campos_obrigatorios = {"dataHora", "status", "pacienteId", "profissionalId"}
    if not campos_obrigatorios.issubset(dados.keys()):
        abort(400, description=f"Campos obrigatórios: {', '.join(campos_obrigatorios)}")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Consulta (dataHora, status, pacienteId, profissionalId) "
        "VALUES (?, ?, ?, ?)",
        (dados["dataHora"], dados["status"], dados["pacienteId"], dados["profissionalId"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    # 201 Created + Location do recurso recém‑criado
    resposta = jsonify({"id": novo_id, **dados})
    resposta.status_code = 201
    resposta.headers["Location"] = f"/Consulta/{novo_id}"
    return resposta

##ROTA UPDATE
#############################################
@consulta_bp.route("/Consulta/<int:id_consulta>", methods=["PUT", "PATCH"])
def atualizar_usuario(id_consulta):
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Para PUT, garanta que todos os campos estejam presentes
    if request.method == "PUT":
        campos_esperados = {"dataHora", "status", "pacienteId", "profissionalId"}
        if not campos_esperados.issubset(dados.keys()):
            abort(400, description=f"PUT requer todos os campos: {', '.join(campos_esperados)}")

    # Monta dinamicamente o SQL somente com os campos enviados
    campos_validos = {"dataHora", "status", "pacienteId", "profissionalId"}
    set_clauses = []
    valores = []
    for campo in campos_validos & dados.keys():
        set_clauses.append(f"{campo} = ?")
        valores.append(dados[campo])

    if not set_clauses:
        abort(400, description="Nenhum campo válido para atualizar")

    valores.append(id_consulta)  # último parâmetro é o WHERE

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE Consulta SET {', '.join(set_clauses)} WHERE id = ?",
        tuple(valores)
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Consulta não encontrada")

    conn.close()
    # 204 = No Content, mas você pode devolver 200 com o JSON atualizado se preferir
    return ("", 204)
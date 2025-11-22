from flask import Blueprint, request, jsonify, abort
from CONECTAR.funcaoConectar import conectar

profissionalSaude_bp = Blueprint("ProfissionalSaude", __name__)

##############################################
#ROTAS PARA A TABELA PROFISSIONAL DA SAÚDE

##ROTA GET
##############################################
@profissionalSaude_bp.route("/ProfissionalSaude", methods=["GET"])
def listar_Cadastros():
    conn = conectar()
    conn.execute("PRAGMA foreign_keys = ON") #ativa as chaves estrangeiras das tabelas (pois, não é ativado por padrão)
    cursor = conn.cursor()
    cursor.execute("SELECT id, especialidade, crm  FROM ProfissionalSaude")
    dados = [
        {"id": row[0], "especialidade": row[1], "crm": row[2] }
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(dados)

##ROTA DELETE
#############################################
from flask import jsonify, abort

@profissionalSaude_bp.route("/ProfissionalSaude/<int:id_ProfissionalSaude>", methods=["DELETE"])
def deletar_ProfissionalSaude(id_ProfissionalSaude):
    conn = conectar()
    cursor = conn.cursor()

    # tenta apagar o registro informado
    cursor.execute("DELETE FROM ProfissionalSaude WHERE id = ?", (id_ProfissionalSaude,))
    conn.commit()

    # cursor.rowcount informa quantas linhas foram afetadas
    if cursor.rowcount == 0:
        conn.close()
        # nenhum registro com esse ID → devolve 404
        abort(404, description="Profissional não encontrado")

    conn.close()
    # 204 = No Content (padrão para deleções bem‑sucedidas)
    return ("", 204)


##ROTA INSERT
#############################################

from flask import request, jsonify, abort
@profissionalSaude_bp.route("/ProfissionalSaude", methods=["POST"])
def criar_ProfissionalSaude():
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Validação de campos obrigatórios
    campos_obrigatorios = {"especialidade", "crm"}
    if not campos_obrigatorios.issubset(dados.keys()):
        abort(400, description=f"Campos obrigatórios: {', '.join(campos_obrigatorios)}")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ProfissionalSaude (especialidade, crm) "
        "VALUES (?, ?)",
        (dados["especialidade"], dados["crm"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    # 201 Created + Location do recurso recém‑criado
    resposta = jsonify({"id": novo_id, **dados})
    resposta.status_code = 201
    resposta.headers["Location"] = f"/ProfissionalSaude/{novo_id}"
    return resposta

##ROTA UPDATE
#############################################
@profissionalSaude_bp.route("/ProfissionalSaude/<int:id_ProfissionalSaude>", methods=["PUT", "PATCH"])
def atualizar_usuario(id_ProfissionalSaude):
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Para PUT, garanta que todos os campos estejam presentes
    if request.method == "PUT":
        campos_esperados = {"especialidade", "crm"}
        if not campos_esperados.issubset(dados.keys()):
            abort(400, description=f"PUT requer todos os campos: {', '.join(campos_esperados)}")

    # Monta dinamicamente o SQL somente com os campos enviados
    campos_validos = {"especialidade", "crm"}
    set_clauses = []
    valores = []
    for campo in campos_validos & dados.keys():
        set_clauses.append(f"{campo} = ?")
        valores.append(dados[campo])

    if not set_clauses:
        abort(400, description="Nenhum campo válido para atualizar")

    valores.append(id_ProfissionalSaude)  # último parâmetro é o WHERE

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE ProfissionalSaude SET {', '.join(set_clauses)} WHERE id = ?",
        tuple(valores)
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Profissional não encontrado")

    conn.close()
    # 204 = No Content, mas você pode devolver 200 com o JSON atualizado se preferir
    return ("", 204)
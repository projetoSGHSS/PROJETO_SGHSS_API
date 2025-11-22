from flask import Blueprint, request, jsonify, abort
from CONECTAR.funcaoConectar import conectar

teleconsulta_bp = Blueprint("Teleconsulta", __name__)

##############################################
#ROTAS PARA A TABELA TELECONSULTA

##ROTA GET
##############################################
@teleconsulta_bp.route("/Teleconsulta", methods=["GET"])
def listar_Teleconsultas():
    conn = conectar()
    conn.execute("PRAGMA foreign_keys = ON") #ativa as chaves estrangeiras das tabelas (pois, não é ativado por padrão)
    cursor = conn.cursor()
    cursor.execute("SELECT id, status, linkAcesso, consultaId  FROM Teleconsulta")
    dados = [
        {"id": row[0], "status": row[1], "linkAcesso": row[2], "consultaId": row[3] }
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(dados)

##ROTA DELETE
#############################################
from flask import jsonify, abort

@teleconsulta_bp.route("/Teleconsulta/<int:id_teleconsulta>", methods=["DELETE"])
def deletar_consulta(id_teleconsulta):
    conn = conectar()
    cursor = conn.cursor()

    # tenta apagar o registro informado
    cursor.execute("DELETE FROM Teleconsulta WHERE id = ?", (id_teleconsulta,))
    conn.commit()

    # cursor.rowcount informa quantas linhas foram afetadas
    if cursor.rowcount == 0:
        conn.close()
        # nenhum registro com esse ID → devolve 404
        abort(404, description="Teleconsulta não encontrada")

    conn.close()
    # 204 = No Content (padrão para deleções bem‑sucedidas)
    return ("", 204)


##ROTA INSERT
#############################################

from flask import request, jsonify, abort
@teleconsulta_bp.route("/Teleconsulta", methods=["POST"])
def criar_teleconsulta():
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Validação de campos obrigatórios
    campos_obrigatorios = {"status", "linkAcesso", "consultaId"}
    if not campos_obrigatorios.issubset(dados.keys()):
        abort(400, description=f"Campos obrigatórios: {', '.join(campos_obrigatorios)}")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Teleconsulta (status, linkAcesso, consultaId) "
        "VALUES (?, ?, ?)",
        (dados["status"], dados["linkAcesso"], dados["consultaId"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    # 201 Created + Location do recurso recém‑criado
    resposta = jsonify({"id": novo_id, **dados})
    resposta.status_code = 201
    resposta.headers["Location"] = f"/Teleconsulta/{novo_id}"
    return resposta

##ROTA UPDATE
#############################################
@teleconsulta_bp.route("/Teleconsulta/<int:id_teleconsulta>", methods=["PUT", "PATCH"])
def atualizar_teleconsulta(id_teleconsulta):
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Para PUT, garanta que todos os campos estejam presentes
    if request.method == "PUT":
        campos_esperados = {"status", "linkAcesso", "consultaId"}
        if not campos_esperados.issubset(dados.keys()):
            abort(400, description=f"PUT requer todos os campos: {', '.join(campos_esperados)}")

    # Monta dinamicamente o SQL somente com os campos enviados
    campos_validos = {"status", "linkAcesso", "consultaId"}
    set_clauses = []
    valores = []
    for campo in campos_validos & dados.keys():
        set_clauses.append(f"{campo} = ?")
        valores.append(dados[campo])

    if not set_clauses:
        abort(400, description="Nenhum campo válido para atualizar")

    valores.append(id_teleconsulta)  # último parâmetro é o WHERE

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE Teleconsulta SET {', '.join(set_clauses)} WHERE id = ?",
        tuple(valores)
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Teleconsulta não encontrada")

    conn.close()
    # 204 = No Content, mas você pode devolver 200 com o JSON atualizado se preferir
    return ("", 204)
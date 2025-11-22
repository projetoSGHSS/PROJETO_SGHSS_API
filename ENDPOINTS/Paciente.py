from flask import Blueprint, request, jsonify, abort
from CONECTAR.funcaoConectar import conectar

paciente_bp = Blueprint("Paciente", __name__)

##############################################
#ROTAS PARA A TABELA PACIENTE

##ROTA GET
##############################################
@paciente_bp.route("/Paciente", methods=["GET"])
def listar_Cadastros():
    conn = conectar()
    conn.execute("PRAGMA foreign_keys = ON") #ativa as chaves estrangeiras das tabelas (pois, não é ativado por padrão)
    cursor = conn.cursor()
    cursor.execute("SELECT id, dataNascimento, historico  FROM Paciente")
    dados = [
        {"id": row[0], "dataNascimento": row[1], "historico": row[2] }
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(dados)

##ROTA DELETE
#############################################
from flask import jsonify, abort

@paciente_bp.route("/Paciente/<int:id_paciente>", methods=["DELETE"])
def deletar_Paciente(id_paciente):
    conn = conectar()
    cursor = conn.cursor()

    # tenta apagar o registro informado
    cursor.execute("DELETE FROM Paciente WHERE id = ?", (id_paciente,))
    conn.commit()

    # cursor.rowcount informa quantas linhas foram afetadas
    if cursor.rowcount == 0:
        conn.close()
        # nenhum registro com esse ID → devolve 404
        abort(404, description="Paciente não encontrado")

    conn.close()
    # 204 = No Content (padrão para deleções bem‑sucedidas)
    return ("", 204)


##ROTA INSERT
#############################################

from flask import request, jsonify, abort
@paciente_bp.route("/Paciente", methods=["POST"])
def criar_Paciente():
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Validação de campos obrigatórios
    campos_obrigatorios = {"dataNascimento", "historico"}
    if not campos_obrigatorios.issubset(dados.keys()):
        abort(400, description=f"Campos obrigatórios: {', '.join(campos_obrigatorios)}")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Paciente (dataNascimento, historico) "
        "VALUES (?, ?)",
        (dados["dataNascimento"], dados["historico"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    # 201 Created + Location do recurso recém‑criado
    resposta = jsonify({"id": novo_id, **dados})
    resposta.status_code = 201
    resposta.headers["Location"] = f"/Paciente/{novo_id}"
    return resposta

##ROTA UPDATE
#############################################
@paciente_bp.route("/Paciente/<int:id_paciente>", methods=["PUT", "PATCH"])
def atualizar_usuario(id_paciente):
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Para PUT, garanta que todos os campos estejam presentes
    if request.method == "PUT":
        campos_esperados = {"dataNascimento", "historico"}
        if not campos_esperados.issubset(dados.keys()):
            abort(400, description=f"PUT requer todos os campos: {', '.join(campos_esperados)}")

    # Monta dinamicamente o SQL somente com os campos enviados
    campos_validos = {"dataNascimento", "historico"}
    set_clauses = []
    valores = []
    for campo in campos_validos & dados.keys():
        set_clauses.append(f"{campo} = ?")
        valores.append(dados[campo])

    if not set_clauses:
        abort(400, description="Nenhum campo válido para atualizar")

    valores.append(id_paciente)  # último parâmetro é o WHERE

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE Paciente SET {', '.join(set_clauses)} WHERE id = ?",
        tuple(valores)
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Paciente não encontrado")

    conn.close()
    # 204 = No Content, mas você pode devolver 200 com o JSON atualizado se preferir
    return ("", 204)
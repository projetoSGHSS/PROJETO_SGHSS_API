from flask import Blueprint, request, jsonify, abort
from CONECTAR.funcaoConectar import conectar

prescricao_bp = Blueprint("Prescricao", __name__)

##############################################
#ROTAS PARA A TABELA PRESCRIÇÃO

##ROTA GET
##############################################
@prescricao_bp.route("/Prescricao", methods=["GET"])
def listar_Prescricao():
    conn = conectar()
    conn.execute("PRAGMA foreign_keys = ON") #ativa as chaves estrangeiras das tabelas (pois, não é ativado por padrão)
    cursor = conn.cursor()
    cursor.execute("SELECT id, medicamento, dosagem, validade, pacienteId, profissionalId  FROM Prescricao")
    dados = [
        {"id": row[0], "medicamento": row[1], "dosagem": row[2], "validade": row[3], "pacienteId": row[4], "profissionalId": row[5] }
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(dados)

##ROTA DELETE
#############################################
from flask import jsonify, abort

@prescricao_bp.route("/Prescricao/<int:id_prescricao>", methods=["DELETE"])
def deletar_Prescricao(id_prescricao):
    conn = conectar()
    cursor = conn.cursor()

    # tenta apagar o registro informado
    cursor.execute("DELETE FROM Prescricao WHERE id = ?", (id_prescricao,))
    conn.commit()

    # cursor.rowcount informa quantas linhas foram afetadas
    if cursor.rowcount == 0:
        conn.close()
        # nenhum registro com esse ID → devolve 404
        abort(404, description="Prescrição não encontrada")

    conn.close()
    # 204 = No Content (padrão para deleções bem‑sucedidas)
    return ("", 204)


##ROTA INSERT
#############################################

from flask import request, jsonify, abort
@prescricao_bp.route("/Prescricao", methods=["POST"])
def criar_Prescricao():
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Validação de campos obrigatórios
    campos_obrigatorios = {"medicamento", "dosagem", "validade", "pacienteId", "profissionalId"}
    if not campos_obrigatorios.issubset(dados.keys()):
        abort(400, description=f"Campos obrigatórios: {', '.join(campos_obrigatorios)}")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Prescricao (medicamento, dosagem, validade, pacienteId, profissionalId) "
        "VALUES (?, ?, ?, ?, ?)",
        (dados["medicamento"], dados["dosagem"], dados["validade"], dados["pacienteID"], dados["profissionalId"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    # 201 Created + Location do recurso recém‑criado
    resposta = jsonify({"id": novo_id, **dados})
    resposta.status_code = 201
    resposta.headers["Location"] = f"/Prescricao/{novo_id}"
    return resposta

##ROTA UPDATE
#############################################
@prescricao_bp.route("/Prescricao/<int:id_prescricao>", methods=["PUT", "PATCH"])
def atualizar_Prescricao(id_prescricao):
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Para PUT, garanta que todos os campos estejam presentes
    if request.method == "PUT":
        campos_esperados = {"medicamento", "dosagem", "validade", "pacienteId", "profissionalId"}
        if not campos_esperados.issubset(dados.keys()):
            abort(400, description=f"PUT requer todos os campos: {', '.join(campos_esperados)}")

    # Monta dinamicamente o SQL somente com os campos enviados
    campos_validos = {"medicamento", "dosagem", "validade", "pacienteId", "profissionalId"}
    set_clauses = []
    valores = []
    for campo in campos_validos & dados.keys():
        set_clauses.append(f"{campo} = ?")
        valores.append(dados[campo])

    if not set_clauses:
        abort(400, description="Nenhum campo válido para atualizar")

    valores.append(id_prescricao)  # último parâmetro é o WHERE

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE Prescricao SET {', '.join(set_clauses)} WHERE id = ?",
        tuple(valores)
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Prescrição não encontrada")

    conn.close()
    # 204 = No Content, mas você pode devolver 200 com o JSON atualizado se preferir
    return ("", 204)
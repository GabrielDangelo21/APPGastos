from flask import Flask, render_template, jsonify, request
from classes import GerenciadorFinancas, Transacao, Conta, Categoria
import sqlite3

app = Flask(__name__)
# Usamos o objeto banco para gerenciar a maioria das operações
banco = GerenciadorFinancas("receitas_despesas.db")


@app.route("/")
def index():
    return render_template("index.html")


# --- ROTAS DE LISTAGEM (GET) ---


@app.route("/api/transacoes", methods=["GET"])
def listar_transacoes():
    try:
        cursor = banco.conn.cursor()
        cursor.execute(
            """
            SELECT t.id, t.data, t.descricao, t.valor, 
                   cat.nome_categoria, c.nome_instituicao
            FROM transacao t
            JOIN categoria cat ON t.id_categoria = cat.id
            JOIN conta c ON t.id_conta = c.id
            ORDER BY t.data DESC
        """
        )
        transacoes = cursor.fetchall()
        lista = [
            {
                "id": t[0],
                "data": t[1],
                "descricao": t[2],
                "valor": t[3],
                "categoria": t[4],
                "conta": t[5],
            }
            for t in transacoes
        ]
        return jsonify(lista)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


@app.route("/api/contas", methods=["GET"])
def listar_contas():
    try:
        cursor = banco.conn.cursor()
        # IMPORTANTE: Pegar saldo e tipo para o modal de edição funcionar
        cursor.execute(
            "SELECT id, nome_instituicao, moeda, saldo_atual, tipo_conta FROM conta"
        )
        contas = [
            {
                "id": row[0],
                "nome_instituicao": row[1],
                "moeda": row[2],
                "saldo": row[3],
                "tipo": row[4],
            }
            for row in cursor.fetchall()
        ]
        return jsonify(contas)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


@app.route("/api/categorias", methods=["GET"])
def listar_categorias():
    try:
        cursor = banco.conn.cursor()
        cursor.execute("SELECT id, nome_categoria, tipo_categoria FROM categoria")
        categorias = [
            {"id": row[0], "nome_categoria": row[1], "tipo": row[2]}
            for row in cursor.fetchall()
        ]
        return jsonify(categorias)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


# --- ROTAS DE SALVAMENTO (POST) ---


@app.route("/api/transacoes", methods=["POST"])
def salvar_transacao():
    dados = request.json
    try:
        nova_transacao_obj = Transacao(
            data=dados["data"],
            descricao=dados["descricao"],
            valor=dados["valor"],
            id_conta=dados["id_conta"],
            id_categoria=dados["id_categoria"],
        )
        banco.adicionar_transacao(nova_transacao_obj)
        return jsonify({"status": "sucesso"}), 201
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


@app.route("/api/contas", methods=["POST"])
def salvar_conta():
    dados = request.json
    try:
        nova_conta = Conta(
            nome_instituicao=dados["nome"],
            moeda=dados["moeda"],
            saldo_inicial=dados["saldo"],
            tipo_conta=dados["tipo"],
        )
        banco.adicionar_conta(nova_conta)
        return jsonify({"status": "sucesso"}), 201
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


@app.route("/api/categorias", methods=["POST"])
def salvar_categoria():
    dados = request.json
    try:
        nova_cat = Categoria(nome_categoria=dados["nome"], tipo_categoria=dados["tipo"])
        banco.adicionar_categoria(nova_cat)
        return jsonify({"status": "sucesso"}), 201
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


# --- ROTAS DE EDIÇÃO E EXCLUSÃO (PUT/DELETE) ---


@app.route("/api/transacoes/<int:id>", methods=["PUT"])
def editar_transacao_web(id):
    dados = request.json
    try:
        banco.editar_transacao(
            id,
            dados["data"],
            dados["descricao"],
            dados["valor"],
            dados["id_conta"],
            dados["id_categoria"],
        )
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


@app.route("/api/transacoes/<int:id>", methods=["DELETE"])
def excluir_transacao(id):
    try:
        cursor = banco.conn.cursor()
        cursor.execute("DELETE FROM transacao WHERE id = ?", (id,))
        banco.conn.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

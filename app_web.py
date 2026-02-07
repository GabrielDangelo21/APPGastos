from flask import Flask, render_template, jsonify, request
from classes import GerenciadorFinancas, Transacao, Conta, Categoria

# REMOVEMOS O IMPORT DO 'db' AQUI POIS ELE NÃO EXISTE NO SEU CLASSES.PY

app = Flask(__name__)

# Instancia o gerenciador que usa o SQLite puro (definido em classes.py)
banco = GerenciadorFinancas("receitas_despesas.db")


@app.route("/")
def index():
    return render_template("index.html")


# --- ROTAS GET ---


@app.route("/api/transacoes", methods=["GET"])
def listar_transacoes():
    try:
        cursor = banco.conn.cursor()
        cursor.execute(
            """
            SELECT 
                t.id, t.data, t.descricao, t.valor, 
                c.nome_categoria as categoria, 
                cta.nome_instituicao as conta,
                t.id_conta, t.id_categoria, cta.moeda
            FROM transacao t
            LEFT JOIN categoria c ON t.id_categoria = c.id
            LEFT JOIN conta cta ON t.id_conta = cta.id
            ORDER BY t.data DESC
        """
        )

        colunas = [col[0] for col in cursor.description]
        transacoes = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        return jsonify(transacoes)
    except Exception as e:
        print(f"Erro Transações: {e}")
        return jsonify([]), 500


@app.route("/api/contas", methods=["GET"])
def listar_contas():
    try:
        cursor = banco.conn.cursor()
        # Buscamos os dados brutos do SQLite
        cursor.execute(
            "SELECT id, nome_instituicao, moeda, saldo_inicial, tipo_conta FROM conta"
        )
        dados = cursor.fetchall()

        # Montamos a lista garantindo os nomes que o JS espera
        contas_formatadas = []
        for linha in dados:
            contas_formatadas.append(
                {
                    "id": linha[0],
                    "nome_instituicao": linha[1],
                    "moeda": linha[2],
                    "saldo_inicial": float(linha[3] or 0),
                    "tipo_conta": linha[4],
                }
            )
        return jsonify(contas_formatadas)
    except Exception as e:
        print(f"Erro ao listar contas: {e}")
        return jsonify([]), 500


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
        return jsonify({"erro": str(e)}), 500


# --- ROTAS POST (SALVAR) ---


@app.route("/api/transacoes", methods=["POST"])
def salvar_transacao():
    dados = request.json
    try:
        # Cria o objeto Transacao usando sua classe
        nova = Transacao(
            data=dados["data"],
            descricao=dados["descricao"],
            valor=dados["valor"],
            id_conta=dados["id_conta"],
            id_categoria=dados["id_categoria"],
        )
        banco.adicionar_transacao(nova)
        return jsonify({"status": "sucesso"}), 201
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route("/api/contas", methods=["POST"])
def salvar_conta():
    dados = request.json
    print(f"Recebido para salvar: {dados}")  # Veja isso no terminal!
    try:
        # Criamos o objeto usando os nomes que vêm do JS
        nova_conta = Conta(
            nome_instituicao=dados.get("nome"),
            moeda=dados.get("moeda"),
            saldo_inicial=float(dados.get("saldo", 0)),
            tipo_conta=dados.get("tipo"),
        )
        banco.adicionar_conta(nova_conta)
        return jsonify({"status": "sucesso"}), 201
    except Exception as e:
        print(f"ERRO AO SALVAR NO PYTHON: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route("/api/categorias", methods=["POST"])
def salvar_categoria():
    dados = request.json
    try:
        nova = Categoria(dados["nome"], dados["tipo"])
        banco.adicionar_categoria(nova)
        return jsonify({"status": "sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# --- ROTAS DELETE ---


@app.route("/api/contas/<int:id>", methods=["DELETE"])
def excluir_conta(id):
    try:
        cursor = banco.conn.cursor()

        # Verificação matemática: se o contador de transações for > 0, bloqueia
        cursor.execute("SELECT COUNT(*) FROM transacao WHERE id_conta = ?", (id,))
        quantidade = cursor.fetchone()[0]

        if quantidade > 0:
            # Retornamos erro 400 (Bad Request) com uma mensagem clara
            return (
                jsonify(
                    {
                        "erro": f"Bloqueado: Esta conta possui {quantidade} transações atreladas. "
                        "Exclua as transações primeiro."
                    }
                ),
                400,
            )

        cursor.execute("DELETE FROM conta WHERE id = ?", (id,))
        banco.conn.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/categorias/<int:id>", methods=["DELETE"])
def excluir_categoria(id):
    try:
        cursor = banco.conn.cursor()
        cursor.execute("DELETE FROM categoria WHERE id = ?", (id,))
        banco.conn.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/transacoes/<int:id>", methods=["DELETE"])
def excluir_transacao(id):
    try:
        banco.excluir_transacao(id)
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# --- ROTAS EDIT ---


@app.route("/api/contas/<int:id>", methods=["PUT"])
def editar_conta(id):
    dados = request.json
    try:
        cursor = banco.conn.cursor()
        cursor.execute(
            """
            UPDATE conta 
            SET nome_instituicao = ?, moeda = ?, saldo_inicial = ?, tipo_conta = ?
            WHERE id = ?
        """,
            (dados["nome"], dados["moeda"], dados["saldo"], dados["tipo"], id),
        )
        banco.conn.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        print(f"Erro ao editar conta: {e}")
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, jsonify, request
from classes import GerenciadorFinancas, Transacao, Categoria

app = Flask(__name__)
# Instancia o banco
banco = GerenciadorFinancas("receitas_despesas.db")


@app.route("/")
def index():
    return render_template("index.html")


# --- ROTA DE CATEGORIAS (Simples e Direta) ---
@app.route("/api/categorias", methods=["GET"])
def listar_categorias():
    try:
        cursor = banco.conn.cursor()
        cursor.execute("SELECT id, nome_categoria, tipo_categoria FROM categoria")
        categorias = [
            {"id": r[0], "nome_categoria": r[1], "tipo": r[2]}
            for r in cursor.fetchall()
        ]
        return jsonify(categorias)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/categorias", methods=["POST"])
def salvar_categoria():
    dados = request.json
    try:
        nova_cat = Categoria(dados["nome"], dados["tipo"])
        banco.adicionar_categoria(nova_cat)
        return jsonify({"status": "sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# --- ROTAS DE TRANSAÇÕES (Sem vínculos com Contas) ---
@app.route("/api/transacoes", methods=["GET"])
def listar_transacoes():
    try:
        cursor = banco.conn.cursor()
        # Query simplificada: Sem JOIN com conta, pegando a moeda direto da transação (se existir)
        # Assumindo que você manteve 'moeda' na transação ou vai usar padrão BRL
        cursor.execute(
            """
            SELECT 
                t.id, t.data, t.descricao, t.valor, 
                c.nome_categoria, t.id_categoria, t.moeda
            FROM transacao t
            JOIN categoria c ON t.id_categoria = c.id
            ORDER BY t.data DESC
        """
        )

        transacoes = []
        for r in cursor.fetchall():
            transacoes.append(
                {
                    "id": r[0],
                    "data": r[1],
                    "descricao": r[2],
                    "valor": r[3],
                    "categoria": r[4],
                    "id_categoria": r[5],
                    "moeda": r[6],
                }
            )
        return jsonify(transacoes)
    except Exception as e:
        print(f"Erro ao listar: {e}")
        return jsonify([]), 500


@app.route("/api/transacoes", methods=["POST"])
def salvar_transacao():
    dados = request.json
    try:
        # Criamos a transação sem ID de conta
        nova_transacao = Transacao(
            data=dados["data"],
            descricao=dados["descricao"],
            valor=float(dados["valor"]),
            moeda=dados.get("moeda", "BRL"),  # Padrão BRL se não vier
            id_categoria=int(dados["categoria_id"]),
        )
        banco.adicionar_transacao(nova_transacao)
        return jsonify({"status": "sucesso"}), 201
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route("/api/transacoes/<int:id>", methods=["DELETE"])
def excluir_transacao_rota(id):
    try:
        banco.excluir_transacao(id)
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# --- NOVAS ROTAS PARA GERENCIAR CATEGORIAS ---


@app.route("/api/categorias/<int:id>", methods=["PUT"])
def editar_categoria(id):
    dados = request.json
    novo_nome = dados["nome"]
    novo_tipo = dados["tipo"]

    try:
        cursor = banco.conn.cursor()

        # 1. Atualiza o nome e o tipo da categoria
        cursor.execute(
            """
            UPDATE categoria 
            SET nome_categoria = ?, tipo_categoria = ?
            WHERE id = ?
        """,
            (novo_nome, novo_tipo, id),
        )

        # 2. AJUSTE AUTOMÁTICO DE VALORES:
        # Se virou Despesa, garantimos que todos os valores sejam negativos
        if novo_tipo == "Despesa":
            cursor.execute(
                """
                UPDATE transacao 
                SET valor = -ABS(valor) 
                WHERE id_categoria = ?
            """,
                (id,),
            )

        # Se virou Receita, garantimos que todos os valores sejam positivos
        elif novo_tipo == "Receita":
            cursor.execute(
                """
                UPDATE transacao 
                SET valor = ABS(valor) 
                WHERE id_categoria = ?
            """,
                (id,),
            )

        banco.conn.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        banco.conn.rollback()
        print(f"Erro ao atualizar categoria: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route("/api/categorias/<int:id>", methods=["DELETE"])
def excluir_categoria(id):
    try:
        cursor = banco.conn.cursor()

        # 1. Verifica se tem transações usando essa categoria
        cursor.execute("SELECT COUNT(*) FROM transacao WHERE id_categoria = ?", (id,))
        qtd = cursor.fetchone()[0]

        if qtd > 0:
            return (
                jsonify(
                    {
                        "erro": f"Essa categoria tem {qtd} transações. Exclua as transações antes."
                    }
                ),
                400,
            )

        # 2. Se estiver livre, exclui
        cursor.execute("DELETE FROM categoria WHERE id = ?", (id,))
        banco.conn.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/transacoes/<int:id>", methods=["PUT"])
def editar_transacao(id):
    dados = request.json
    try:
        cursor = banco.conn.cursor()

        # 1. Pegamos o tipo da categoria para garantir o sinal do valor
        cursor.execute(
            "SELECT tipo_categoria FROM categoria WHERE id = ?",
            (dados["categoria_id"],),
        )
        tipo = cursor.fetchone()[0]

        valor = float(dados["valor"])
        if tipo == "Despesa":
            valor = -abs(valor)
        else:
            valor = abs(valor)

        # 2. Atualizamos a transação
        cursor.execute(
            """
            UPDATE transacao 
            SET data = ?, descricao = ?, valor = ?, moeda = ?, id_categoria = ?
            WHERE id = ?
        """,
            (
                dados["data"],
                dados["descricao"],
                valor,
                dados["moeda"],
                dados["categoria_id"],
                id,
            ),
        )

        banco.conn.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

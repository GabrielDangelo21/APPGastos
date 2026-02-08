from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Nome do arquivo onde os dados serão salvos
ARQUIVO_DADOS = "dados.json"

# --- FUNÇÕES AUXILIARES (Para ler e salvar no JSON) ---


def carregar_dados():
    """Lê o arquivo JSON. Se não existir, cria a estrutura padrão."""
    if not os.path.exists(ARQUIVO_DADOS):
        dados_iniciais = {
            "transacoes": [],
            "categorias": [
                {"id": 1, "nome": "Alimentação", "tipo": "Despesa"},
                {"id": 2, "nome": "Salário", "tipo": "Receita"},
                {"id": 3, "nome": "Lazer", "tipo": "Despesa"},
            ],
        }
        salvar_dados(dados_iniciais)
        return dados_iniciais

    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"transacoes": [], "categorias": []}


def salvar_dados(dados):
    """Escreve os dados no arquivo JSON."""
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def gerar_novo_id(lista_itens):
    """Simula o AutoIncrement do banco de dados"""
    if not lista_itens:
        return 1
    # Pega o maior ID existente e soma 1
    return max(item["id"] for item in lista_itens) + 1


# --- ROTAS DA APLICAÇÃO ---


@app.route("/")
def index():
    return render_template("index.html")


# --- API: TRANSAÇÕES ---


@app.route("/api/transacoes", methods=["GET"])
def get_transacoes():
    dados = carregar_dados()
    # Adicionamos o nome da categoria em cada transação para facilitar o frontend
    lista_completa = []

    # Cria um dicionário para achar nomes de categorias rápido: {1: "Alimentação", 2: "Salário"}
    mapa_categorias = {c["id"]: c["nome"] for c in dados["categorias"]}

    for t in dados["transacoes"]:
        t_copia = t.copy()
        # Se a categoria existir, coloca o nome, senão "Desconhecida"
        t_copia["categoria"] = mapa_categorias.get(t["categoria_id"], "Desconhecida")
        lista_completa.append(t_copia)

    return jsonify(lista_completa)


@app.route("/api/transacoes", methods=["POST"])
def add_transacao():
    novo_item = request.json
    dados = carregar_dados()

    # Cria a nova transação
    nova_transacao = {
        "id": gerar_novo_id(dados["transacoes"]),
        "data": novo_item["data"],
        "valor": float(novo_item["valor"]),
        "descricao": novo_item["descricao"],
        "moeda": novo_item["moeda"],
        "categoria_id": int(novo_item["categoria_id"]),
    }

    dados["transacoes"].append(nova_transacao)
    salvar_dados(dados)

    return jsonify({"mensagem": "Transação salva!", "id": nova_transacao["id"]}), 201


@app.route("/api/transacoes/<int:id>", methods=["DELETE"])
def delete_transacao(id):
    dados = carregar_dados()

    # Filtra a lista mantendo apenas quem NÃO tem o ID informado
    nova_lista = [t for t in dados["transacoes"] if t["id"] != id]

    if len(nova_lista) == len(dados["transacoes"]):
        return jsonify({"erro": "Transação não encontrada"}), 404

    dados["transacoes"] = nova_lista
    salvar_dados(dados)
    return jsonify({"mensagem": "Deletado com sucesso"})


@app.route("/api/transacoes/<int:id>", methods=["PUT"])
def edit_transacao(id):
    item_editado = request.json
    dados = carregar_dados()

    for t in dados["transacoes"]:
        if t["id"] == id:
            t["data"] = item_editado["data"]
            t["valor"] = float(item_editado["valor"])
            t["descricao"] = item_editado["descricao"]
            t["moeda"] = item_editado["moeda"]
            t["categoria_id"] = int(item_editado["categoria_id"])

            salvar_dados(dados)
            return jsonify({"mensagem": "Atualizado com sucesso"})

    return jsonify({"erro": "Transação não encontrada"}), 404


# --- API: CATEGORIAS ---


@app.route("/api/categorias", methods=["GET"])
def get_categorias():
    dados = carregar_dados()
    # Mapeamos para retornar "nome_categoria" para compatibilidade com seu JS antigo
    resultado = []
    for c in dados["categorias"]:
        resultado.append(
            {
                "id": c["id"],
                "nome_categoria": c["nome"],  # O JS espera 'nome_categoria'
                "tipo": c.get("tipo", "Despesa"),
            }
        )
    return jsonify(resultado)


@app.route("/api/categorias", methods=["POST"])
def add_categoria():
    nova_cat_req = request.json
    dados = carregar_dados()

    nova_categoria = {
        "id": gerar_novo_id(dados["categorias"]),
        "nome": nova_cat_req["nome"],
        "tipo": nova_cat_req["tipo"],
    }

    dados["categorias"].append(nova_categoria)
    salvar_dados(dados)
    return jsonify({"mensagem": "Categoria criada!"}), 201


@app.route("/api/categorias/<int:id>", methods=["DELETE"])
def delete_categoria(id):
    dados = carregar_dados()

    # Verifica se tem transação usando essa categoria
    tem_uso = any(t["categoria_id"] == id for t in dados["transacoes"])
    if tem_uso:
        return jsonify({"erro": "Não é possível excluir: Categoria em uso!"}), 400

    nova_lista = [c for c in dados["categorias"] if c["id"] != id]
    dados["categorias"] = nova_lista
    salvar_dados(dados)

    return jsonify({"mensagem": "Categoria excluída"})


@app.route("/api/categorias/<int:id>", methods=["PUT"])
def edit_categoria(id):
    req = request.json
    dados = carregar_dados()

    for c in dados["categorias"]:
        if c["id"] == id:
            c["nome"] = req["nome"]
            c["tipo"] = req["tipo"]
            salvar_dados(dados)
            return jsonify({"mensagem": "Categoria atualizada"})

    return jsonify({"erro": "Categoria não encontrada"}), 404


if __name__ == "__main__":
    # Cria o arquivo vazio ao iniciar, se não existir
    carregar_dados()
    app.run(debug=True)

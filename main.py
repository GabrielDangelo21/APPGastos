import sqlite3


class Conta:
    def __init__(
        self, nome_instituicao, moeda, saldo_incial, tipo_conta, id_conta=None
    ):
        self.id_conta = id_conta
        self.nome_instituicao = nome_instituicao
        self.moeda = moeda
        self.saldo_inicial = saldo_incial
        self.tipo_conta = tipo_conta


class Categoria:
    def __init__(self, nome_categoria, tipo_categoria, id_categoria=None):
        self.id_categoria = id_categoria
        self.nome = nome_categoria
        self.tipo = tipo_categoria


class Transacao:
    def __init__(
        self,
        data,
        descricao,
        valor,
        conta_recebida,
        categoria_recebida,
        id_transacao=None,
    ):
        self.id_transacao = id_transacao
        self.data = data
        self.descricao = descricao
        self.valor = valor
        self.conta = conta_recebida
        self.categoria = categoria_recebida


class GerenciadorFinancas:
    def __init__(self, nome_banco):
        self.nome_banco = nome_banco
        self.conn = sqlite3.connect(self.nome_banco)
        self.criando_tabela()

    def criando_tabela(self):

        cursor = self.conn.cursor()

        # 3. Criar tabelas
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_instituicao TEXT NOT NULL,
                moeda TEXT NOT NULL,
                saldo_inicial REAL,
                tipo_conta TEXT NOT NULL  
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_categoria TEXT NOT NULL,
                tipo_categoria TEXT NOT NULL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE,
                descricao TEXT NOT NULL,
                valor REAL,
                id_conta INTEGER,
                id_categoria INTEGER,
                FOREIGN KEY (id_conta) REFERENCES conta(id),
                FOREIGN KEY (id_categoria) REFERENCES categoria(id)
            )
        """
        )

        self.conn.commit()

    def adicionar_conta(self, conta_obj):
        cursor = self.conn.cursor()

        # 1. Verificar se a conta já existe (pelo nome)
        cursor.execute(
            "SELECT id FROM conta WHERE nome_instituicao = ?",
            (conta_obj.nome_instituicao,),
        )
        if cursor.fetchone():
            print(f"A conta '{conta_obj.nome_instituicao}' já existe no banco.")
        else:
            # 2. Inserir usando os dados do objeto
            cursor.execute(
                """
                INSERT INTO conta (nome_instituicao, moeda, saldo_inicial, tipo_conta) 
                VALUES (?, ?, ?, ?)
            """,
                (
                    conta_obj.nome_instituicao,
                    conta_obj.moeda,
                    conta_obj.saldo_inicial,
                    conta_obj.tipo_conta,
                ),
            )

            self.conn.commit()
            print(f"Conta '{conta_obj.nome_instituicao}' cadastrada com sucesso!")

    def adicionar_categoria(self, categoria_obj):
        cursor = self.conn.cursor()

        # 1. Verificar se a categoria já existe (pelo nome)
        cursor.execute(
            "SELECT id FROM categoria WHERE nome_categoria = ?", (categoria_obj.nome,)
        )
        if cursor.fetchone():
            print(f"A categoria '{categoria_obj.nome}' já existe no banco.")
        else:
            # 2. Inserir usando os dados do objeto
            cursor.execute(
                """
                INSERT INTO categoria (nome_categoria, tipo_categoria) 
                VALUES (?, ?)
            """,
                (categoria_obj.nome, categoria_obj.tipo),
            )

            self.conn.commit()
            print(f"Categoria '{categoria_obj.nome}' cadastrada com sucesso!")

    def buscar_id_conta(self, nome_procurado):
        cursor = self.conn.cursor()

        # 1. Executa a busca
        cursor.execute(
            "SELECT id FROM conta WHERE nome_instituicao = ?", (nome_procurado,)
        )

        # 2. Pega a primeira linha encontrada
        resultado = cursor.fetchone()

        if resultado:
            # Se encontrou, resultado será algo como (1,)
            return resultado[0]  # Retorna apenas o número 1
        else:
            print(f"Nenhuma conta com o nome '{nome_procurado}' encontrada.")
            return None

    def buscar_id_categoria(self, nome_procurado):
        cursor = self.conn.cursor()

        # 1. Executa a busca
        cursor.execute(
            "SELECT id FROM categoria WHERE nome_categoria = ?", (nome_procurado,)
        )

        # 2. Pega a primeira linha encontrada
        resultado = cursor.fetchone()

        if resultado:
            # Se encontrou, resultado será algo como (1,)
            return resultado[0]  # Retorna apenas o número 1
        else:
            print(f"Nenhuma categoria com o nome '{nome_procurado}' encontrada.")
            return None

    def adicionar_transacao(self, transacao_obj):
        id_conta = self.buscar_id_conta(transacao_obj.conta)
        id_categoria = self.buscar_id_categoria(transacao_obj.categoria)

        cursor = self.conn.cursor()

        if not id_conta or not id_categoria:
            print(
                f"Erro: Verifique se a conta '{transacao_obj.conta}' e a categoria '{transacao_obj.categoria}' estão cadastradas."
            )
        else:
            cursor.execute(
                "INSERT INTO transacao (data, descricao, valor, id_conta, id_categoria) VALUES (?, ?, ?, ?, ?)",
                (
                    transacao_obj.data,
                    transacao_obj.descricao,
                    transacao_obj.valor,
                    id_conta,
                    id_categoria,
                ),
            )

            self.conn.commit()
            print(f"Transação '{transacao_obj.descricao}' adicionada com sucesso!")

    def total_gastos_por_categoria(self, nome_categoria):
        id_categoria = self.buscar_id_categoria(nome_categoria.nome)

        cursor = self.conn.cursor()

        if not id_categoria:
            print(f"Erro: A categoria '{nome_categoria.nome}' não existe.")
            return 0
        else:
            cursor.execute(
                "SELECT SUM(valor) FROM transacao WHERE id_categoria = ?",
                (id_categoria,),
            )

            # Pega o resultado da soma
            resultado = cursor.fetchone()

            # Se não houver transações, o SUM retorna None.
            # Por isso, usamos um "ou 0" para não dar erro.
            soma_total = resultado[0] if resultado[0] else 0

            return print(soma_total)

    # def mostrar_transacao(self):
    #     cursor = self.conn.cursor()
    #     cursor.execute("SELECT * FROM transacao")
    #     resultado = cursor.fetchall()
    #     print(resultado)

    print("Banco de dados e tabela criados com sucesso.")


banco = GerenciadorFinancas("receitas_despesas.db")
itau = Conta("Itaú", "BRL", 0, "Corrente")
alimentacao = Categoria("Alimentação", "Despesa")

banco.adicionar_conta(itau)
banco.adicionar_categoria(alimentacao)

compra = Transacao(
    "2026-02-03", "Churros", 2.5, itau.nome_instituicao, alimentacao.nome
)

banco.adicionar_transacao(compra)
banco.total_gastos_por_categoria(alimentacao)
banco.mostrar_transacao()

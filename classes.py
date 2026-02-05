import locale
import sqlite3


class Conta:
    def __init__(
        self, nome_instituicao, moeda, saldo_inicial, tipo_conta, id_conta=None
    ):
        self.id_conta = id_conta
        self.nome_instituicao = nome_instituicao
        self.moeda = moeda
        self.saldo_inicial = saldo_inicial
        self.tipo_conta = tipo_conta


class Categoria:
    def __init__(self, nome_categoria, tipo_categoria, id_categoria=None):
        self.id_categoria = id_categoria
        self.nome = nome_categoria
        self.tipo = tipo_categoria


class Transacao:
    def __init__(
        self, data, descricao, valor, id_conta, id_categoria, id_transacao=None
    ):
        self.id_transacao = id_transacao
        self.data = data
        self.descricao = descricao
        self.valor = valor
        self.id_conta = id_conta  # Antes era conta_recebida
        self.id_categoria = id_categoria  # Antes era categoria_recebida


class GerenciadorFinancas:
    def __init__(self, nome_banco):
        self.nome_banco = nome_banco
        self.conn = sqlite3.connect(self.nome_banco)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.criando_tabela()

    def formatar_moeda(self, valor, moeda_codigo):
        # Dicionário de símbolos
        simbolos = {"BRL": "R$", "EUR": "€", "USD": "$"}

        simbolo = simbolos.get(moeda_codigo.upper(), "€")  # Padrão é € se não achar

        # Formatação numérica: 1.250,30
        # Usamos o locale apenas para a parte numérica (separadores de milhar e decimal)
        valor_f = locale.format_string("%.2f", valor, grouping=True)

        return f"{simbolo} {valor_f}"

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

    def exibir_contas(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT nome_instituicao, moeda, saldo_inicial, tipo_conta FROM conta
        """
        )

        resultado = cursor.fetchall()
        for nome_instituicao, moeda, saldo_inicial, tipo_conta in resultado:
            valor_formatado = self.formatar_moeda(saldo_inicial, moeda)
            print(
                f"Banco: {nome_instituicao} | Moeda: {moeda} | Saldo: {valor_formatado} | Tipo: {tipo_conta}"
            )

    def exibir_contas_com_id(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT id, nome_instituicao, moeda, saldo_inicial, tipo_conta FROM conta
        """
        )

        resultado = cursor.fetchall()
        for id, nome_instituicao, moeda, saldo_inicial, tipo_conta in resultado:
            valor_formatado = self.formatar_moeda(saldo_inicial, moeda)
            print(
                f"ID: {id} | Banco: {nome_instituicao} | Moeda: {moeda} | Saldo: {valor_formatado} | Tipo: {tipo_conta}"
            )

    def editar_conta(self, id_conta, nome, moeda, saldo, tipo):
        cursor = self.conn.cursor()
        cursor.execute(
            """
                UPDATE conta 
                SET nome_instituicao = ?, moeda = ?, saldo_inicial = ?, tipo_conta = ?
                WHERE id = ?
            """,
            (nome, moeda, saldo, tipo, id_conta),
        )
        self.conn.commit()
        print(f"\n✅ Conta ID {id_conta} atualizada com sucesso!")

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

    def exibir_categorias(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT nome_categoria, tipo_categoria FROM categoria
        """
        )

        resultado = cursor.fetchall()
        for nome_categoria, tipo_categoria in resultado:
            print(f"Categoria: {nome_categoria} | Tipo: {tipo_categoria}")

    def exibir_categorias_com_id(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome_categoria, tipo_categoria FROM categoria")
        resultado = cursor.fetchall()

        print(f"\n{'ID':<5} | {'NOME':<20} | {'TIPO':<15}")
        print("-" * 45)
        for id_cat, nome, tipo in resultado:
            # Dica: Se quiser que Receita apareça em verde e Despesa em vermelho no terminal:
            # Isso depende do SO, mas o alinhamento abaixo já ajuda muito!
            print(f"{id_cat:<5} | {nome:<20} | {tipo:<15}")

    def editar_categoria(self, id_categoria, nome, tipo):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE categoria 
            SET nome_categoria = ?, tipo_categoria = ?
            WHERE id = ?
        """,
            (nome, tipo, id_categoria),
        )
        self.conn.commit()
        print(f"✅ Categoria ID {id_categoria} atualizada com sucesso!")

    def listar_nome_categorias(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT nome_categoria, tipo_categoria FROM categoria
        """
        )

        resultado = cursor.fetchall()
        for nome_categoria, tipo_categoria in resultado:
            print(f"Categoria: {nome_categoria}")

    def buscar_nome_categoria_por_id(self, id_categoria):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT nome_categoria FROM categoria WHERE id = ?", (id_categoria,)
        )
        resultado = cursor.fetchone()
        return resultado[0] if resultado else "Desconhecida"

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

    def adicionar_transacao(self, transacao):
        cursor = self.conn.cursor()
        # Agora inserimos diretamente os IDs que vieram do objeto transacao
        cursor.execute(
            "INSERT INTO transacao (data, descricao, valor, id_conta, id_categoria) VALUES (?, ?, ?, ?, ?)",
            (
                transacao.data,
                transacao.descricao,
                transacao.valor,
                transacao.id_conta,  # Aqui agora já é o ID
                transacao.id_categoria,  # Aqui agora já é o ID
            ),
        )
        self.conn.commit()
        print(f"Transação '{transacao.descricao}' adicionada com sucesso!")

    def total_gastos_por_categoria(self, nome_categoria):
        id_categoria = self.buscar_id_categoria(nome_categoria)

        if not id_categoria:
            print(f"Erro: A categoria '{nome_categoria}' não existe.")
            return 0

        cursor = self.conn.cursor()

        # O SQL agora busca a soma E a moeda, agrupando-as
        cursor.execute(
            """
            SELECT SUM(t.valor), c.moeda
            FROM transacao t
            JOIN conta c ON t.id_conta = c.id
            WHERE t.id_categoria = ?
            GROUP BY c.moeda
            """,
            (id_categoria,),
        )

        resultados = cursor.fetchall()

        if not resultados:
            print(f"Nenhum gasto registrado na categoria '{nome_categoria}'.")
            return 0

        print(f"\n--- Resumo: {nome_categoria} ---")
        for soma, moeda in resultados:
            print(f"Total em {moeda}: {self.formatar_moeda(soma, moeda)}")

        # Retornamos os resultados (uma lista de tuplas) caso queira usar depois
        return resultados

    def exibir_transacao(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
                SELECT t.data, t.descricao, t.valor, c.nome_instituicao, cat.nome_categoria, c.moeda
                FROM transacao t
                JOIN conta c ON t.id_conta = c.id
                JOIN categoria cat ON t.id_categoria = cat.id
                ORDER BY t.data DESC
            """
        )

        resultado = cursor.fetchall()

        # Cabeçalho para alinhar (lembra da dica do alinhamento?)
        print(
            f"\n{'DATA':<12} | {'DESCRIÇÃO':<20} | {'VALOR':>15} | {'BANCO':<15} | {'CATEGORIA':<15}"
        )
        print("-" * 90)

        for (
            data,
            descricao,
            valor,
            nome_instituicao,
            nome_categoria,
            moeda,
        ) in resultado:
            valor_formatado = self.formatar_moeda(valor, moeda)
            # Usando f-string com alinhamento para ficar bonito
            print(
                f"{str(data):<12} | {descricao[:20].ljust(20)} | {valor_formatado.rjust(15)} | {nome_instituicao[:15].ljust(15)} | {nome_categoria[:15].ljust(15)}"
            )

    def exibir_transacao_com_id(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
                SELECT t.id, t.data, t.descricao, t.valor, c.nome_instituicao, cat.nome_categoria, c.moeda
                FROM transacao t
                JOIN conta c ON t.id_conta = c.id
                JOIN categoria cat ON t.id_categoria = cat.id
                ORDER BY t.data DESC
            """
        )

        resultado = cursor.fetchall()

        # Cabeçalho para alinhar (lembra da dica do alinhamento?)
        print(
            f"\n{'ID':<5} | {'DATA':<12} | {'DESCRIÇÃO':<20} | {'VALOR':>15} | {'BANCO':<15} | {'CATEGORIA':<15}"
        )
        print("-" * 90)

        for (
            id,
            data,
            descricao,
            valor,
            nome_instituicao,
            nome_categoria,
            moeda,
        ) in resultado:
            valor_formatado = self.formatar_moeda(valor, moeda)
            # Usando f-string com alinhamento para ficar bonito
            print(
                f"{str(id):<5} | {str(data):<12} | {descricao[:20].ljust(20)} | {valor_formatado.rjust(15)} | {nome_instituicao[:15].ljust(15)} | {nome_categoria[:15].ljust(15)}"
            )

    def editar_transacao(
        self, id_transacao, data, descricao, valor, id_conta, id_categoria
    ):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE transacao
            SET data = ?, descricao = ?, valor = ?, id_conta = ?, id_categoria = ?
            WHERE id = ?
        """,
            (data, descricao, valor, id_conta, id_categoria, id_transacao),
        )
        self.conn.commit()
        print(f"\n✅ Transação ID {id_transacao} atualizada com sucesso!")

    def excluir_transacao(self, id_transacao):
        cursor = self.conn.cursor()
        # Primeiro verificamos se ela existe para dar um feedback melhor
        cursor.execute("SELECT id FROM transacao WHERE id = ?", (id_transacao,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM transacao WHERE id = ?", (id_transacao,))
            self.conn.commit()
            print(f"✅ Transação ID {id_transacao} removida com sucesso!")
        else:
            print(f"❌ Erro: Transação ID {id_transacao} não encontrada.")

    print("Banco de dados e tabela criados com sucesso.")

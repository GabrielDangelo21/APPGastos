from classes import Categoria, GerenciadorFinancas, Transacao
from leitores import ler_data, ler_data_ou_vazio, ler_float, ler_int, ler_str

banco = GerenciadorFinancas("receitas_despesas.db")


def menu_cadastrar_categoria():
    nome_categoria = ler_str("Categoria: ").strip().title()

    # Nova lógica para o Tipo
    while True:
        print("\nTipo da Categoria:")
        print("1. Receita")
        print("2. Despesa")
        escolha = input("Escolha (1 ou 2): ")

        if escolha == "1":
            tipo_categoria = "Receita"
            break
        elif escolha == "2":
            tipo_categoria = "Despesa"
            break
        else:
            print("❌ Opção inválida! Digite 1 para Receita ou 2 para Despesa.")

    nova_categoria = Categoria(nome_categoria, tipo_categoria)
    banco.adicionar_categoria(nova_categoria)


def menu_cadastrar_transacao():
    print("\n--- NOVA TRANSAÇÃO ---")
    data = ler_data("Data (YYYY-MM-DD): ")
    descricao = ler_str("Descrição: ")
    valor = ler_float("Valor: ")
    while True:
        print("\nQual a moeda da conta?")
        print("1. BRL (R$)")
        print("2. EUR (€)")
        escolha_moeda = input("Escolha (1 ou 2): ")
        if escolha_moeda == "1":
            moeda = "BRL"
            break
        elif escolha_moeda == "2":
            moeda = "EUR"
            break
        print("❌ Opção inválida!")

    while True:
        cursor = banco.conn.cursor()

        # Seleção de Categoria
        print("\nCategorias disponíveis:")
        banco.exibir_categorias_com_id()  # Certifique-se de ter essa função criada
        while True:
            id_categoria = ler_int("Digite o ID da Categoria: ")
            cursor.execute("SELECT id FROM categoria WHERE id = ?", (id_categoria,))
            if cursor.fetchone():
                break
            print("❌ ID de categoria inválido!")

        nova_transacao = Transacao(data, descricao, valor, moeda, id_categoria)
        banco.adicionar_transacao(nova_transacao)
        break


def menu_exibir_categorias():
    banco.exibir_categorias()


def menu_exibir_transacoes():
    banco.exibir_transacao()


def menu_editar_categoria():
    print("\n--- EDITAR CATEGORIA ---")
    # Exibe as categorias com ID para o utilizador saber qual escolher
    banco.exibir_categorias_com_id()

    id_alvo = ler_int("\nDigite o ID da categoria que deseja editar: ")

    # Busca os dados atuais
    cursor = banco.conn.cursor()
    cursor.execute(
        "SELECT nome_categoria, tipo_categoria FROM categoria WHERE id = ?", (id_alvo,)
    )
    atual = cursor.fetchone()

    if not atual:
        print("❌ Erro: Categoria com ID não encontrada.")
        return

    print(f"\nEditando Categoria: {atual[0]}")
    print("(Pressione ENTER para manter o valor atual)")

    # 1. NOVO NOME
    novo_nome = input(f"Novo nome [{atual[0]}]: ").strip().title() or atual[0]

    # 2. NOVO TIPO (Lógica de 1 ou 2)
    while True:
        print(f"Tipo atual: {atual[1]}")
        print("1. Receita")
        print("2. Despesa")
        escolha = input(f"Novo tipo (ou Enter para manter): ")

        if not escolha:
            novo_tipo = atual[1]
            break
        elif escolha == "1":
            novo_tipo = "Receita"
            break
        elif escolha == "2":
            novo_tipo = "Despesa"
            break
        else:
            print("❌ Opção inválida! Digite 1, 2 ou pressione Enter.")

    # 3. ATUALIZAR NO BANCO
    # Certifica-te que tens o método atualizar_categoria no teu classes.py
    banco.editar_categoria(id_alvo, novo_nome, novo_tipo)


def menu_editar_transacao():
    print("\n--- EDITAR TRANSAÇÃO ---")
    banco.exibir_transacao_com_id()

    id_alvo = ler_int("\nDigite o ID da transação que deseja editar: ")

    cursor = banco.conn.cursor()
    # Puxamos os dados atuais
    cursor.execute(
        "SELECT data, descricao, valor, moeda, id_categoria FROM transacao WHERE id = ?",
        (id_alvo,),
    )
    atual = cursor.fetchone()

    if not atual:
        print("❌ ID da transação não encontrado.")
        return

    print(f"\nEditando Transação #{id_alvo}")
    print("(Pressione ENTER para manter o valor atual)")

    # 1. DATA (Usando a nova função)
    nova_data = ler_data_ou_vazio(f"Nova data [{atual[0]}]: ") or atual[0]

    # 2. DESCRIÇÃO
    nova_descricao = input(f"Nova descrição [{atual[1]}]: ") or atual[1]

    # 3. VALOR
    novo_valor_str = input(f"Novo valor [{atual[2]}]: ")
    novo_valor = float(novo_valor_str.replace(",", ".")) if novo_valor_str else atual[2]

    # 4. Moeda
    #     # Seleção de Moeda (Blindada)
    while True:
        print(f"Moeda atual: {atual[3]}")
        print("1. BRL (R$) | 2. EUR (€)")
        escolha_m = input(f"Nova moeda (ou Enter para manter): ")
        if not escolha_m:
            nova_moeda = atual[3]
            break
        elif escolha_m == "1":
            nova_moeda = "BRL"
            break
        elif escolha_m == "2":
            nova_moeda = "EUR"
            break
        print("❌ Opção inválida! Escolha 1, 2 ou Enter.")

    # 5. CATEGORIA (Com validação de existência!)
    banco.exibir_categorias_com_id()
    while True:
        novo_id_categoria_str = input(f"Novo ID Categoria [{atual[4]}]: ")
        if not novo_id_categoria_str:
            novo_id_categoria = atual[4]
            break

        # Verifica se esse ID de categoria existe no banco
        cursor.execute(
            "SELECT id FROM categoria WHERE id = ?", (novo_id_categoria_str,)
        )
        if cursor.fetchone():
            novo_id_categoria = int(novo_id_categoria_str)
            break
        else:
            print(f"❌ Erro: A categoria com ID {novo_id_categoria_str} não existe.")

    # Salva tudo
    banco.editar_transacao(
        id_alvo, nova_data, nova_descricao, novo_valor, nova_moeda, novo_id_categoria
    )


def menu_excluir_transacao():
    print("\n--- EXCLUIR TRANSAÇÃO ---")
    banco.exibir_transacao_com_id()  # Mostra a lista para o usuário saber o ID

    id_alvo = ler_int("\nDigite o ID da transação que deseja excluir: ")

    # Confirmação de segurança
    certeza = input(
        f"Tem certeza que deseja apagar a transação {id_alvo}? (S/N): "
    ).upper()

    if certeza == "S":
        banco.excluir_transacao(id_alvo)
    else:
        print("Operação cancelada.")


def menu_total_gasto_por_categoria():
    print("\n--- TOTAL DE GASTOS POR CATEGORIA ---")
    banco.exibir_categorias_com_id()  # O utilizador vê os IDs
    id_cat = ler_int("\nDigite o ID da categoria: ")

    # Buscamos o nome apenas para mostrar no ecrã
    nome_cat = banco.buscar_nome_categoria_por_id(id_cat)

    # Chama a função de soma que já criámos antes
    banco.total_gastos_por_categoria(id_cat, nome_cat)

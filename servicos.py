from classes import Categoria, Conta, GerenciadorFinancas, Transacao
from leitores import ler_data, ler_float, ler_int, ler_str

banco = GerenciadorFinancas("receitas_despesas.db")


def menu_cadastrar_conta():
    nome_conta = ler_str("Instituição: ")
    moeda = ler_str("Moeda: (BRL / EUR) ")
    saldo = ler_float("Saldo Inicial: ")
    tipo = ler_str("Tipo: (Corrente / Poupança / Cartão de crédito) ")

    nova_conta = Conta(nome_conta, moeda, saldo, tipo)

    banco.adicionar_conta(nova_conta)


def menu_cadastrar_categoria():
    nome_categoria = ler_str("Categoria: ")
    tipo_categoria = ler_str("Tipo: (Receita / Despesa) ")

    nova_categoria = Categoria(nome_categoria, tipo_categoria)

    banco.adicionar_categoria(nova_categoria)


def menu_cadastrar_transacao():
    data = ler_data("Data: YYYY-MM-DD ")
    descricao = ler_str("Descrição: ")
    valor = ler_float("Valor: ")
    nome_instituicao = ler_str("Banco: ")
    categoria_transacao = ler_str("Categoria: ")

    nova_transacao = Transacao(
        data, descricao, valor, nome_instituicao, categoria_transacao
    )

    banco.adicionar_transacao(nova_transacao)


def menu_exibir_contas():
    banco.exibir_contas()


def menu_exibir_categoria():
    banco.exibir_categorias()


def menu_exibir_transacao():
    banco.exibir_transacao()


def menu_editar_conta():
    print("\n--- EDITAR CONTA ---")
    banco.exibir_contas_com_id()

    id_alvo = ler_int("\nDigite o ID da conta que deseja editar: ")

    # Buscamos os dados atuais para mostrar ao usuário
    cursor = banco.conn.cursor()
    cursor.execute(
        "SELECT nome_instituicao, moeda, saldo_inicial, tipo_conta FROM conta WHERE id = ?",
        (id_alvo,),
    )
    atual = cursor.fetchone()

    if not atual:
        print("❌ ID não encontrado.")
        return

    print(f"\nEditando: {atual[0]}")
    print("(Pressione ENTER para manter o valor atual)")

    # Lógica: se o input for vazio, usa o que já está no banco (atual[x])
    novo_nome = input(f"Novo nome [{atual[0]}]: ") or atual[0]
    nova_moeda = input(f"Nova moeda [{atual[1]}]: ") or atual[1]

    # Para números, precisamos de um cuidado extra
    novo_saldo_str = input(f"Novo saldo [{atual[2]}]: ")
    novo_saldo = float(novo_saldo_str.replace(",", ".")) if novo_saldo_str else atual[2]

    novo_tipo = input(f"Novo tipo [{atual[3]}]: ") or atual[3]

    banco.editar_conta(id_alvo, novo_nome, nova_moeda, novo_saldo, novo_tipo)


def menu_editar_categoria():
    print("\n--- EDITAR CATEGORIA ---")
    banco.exibir_categorias_com_id()

    id_alvo = ler_int("\nDigite o ID da categoria que deseja editar: ")

    # Buscamos os dados atuais para mostrar ao usuário
    cursor = banco.conn.cursor()
    cursor.execute(
        "SELECT nome_categoria, tipo_categoria FROM categoria WHERE id = ?",
        (id_alvo,),
    )
    atual = cursor.fetchone()

    if not atual:
        print("❌ ID não encontrado.")
        return

    print(f"\nEditando: {atual[0]}")
    print("(Pressione ENTER para manter o valor atual)")

    # Lógica: se o input for vazio, usa o que já está no banco (atual[x])
    novo_nome = input(f"Nova categoria [{atual[0]}]: ") or atual[0]
    novo_tipo = input(f"Novo tipo [{atual[1]}]: (Receita / Despesa) ") or atual[1]

    banco.editar_categoria(id_alvo, novo_nome, novo_tipo)


def menu_editar_transacao():
    print("\n--- EDITAR TRANSAÇÃO ---")
    banco.exibir_transacao_com_id()

    id_alvo = ler_int("\nDigite o ID da conta que deseja editar: ")

    # Buscamos os dados atuais para mostrar ao usuário
    cursor = banco.conn.cursor()
    cursor.execute(
        "SELECT data, descricao, valor, id_conta, id_categoria FROM transacao WHERE id = ?",
        (id_alvo,),
    )
    atual = cursor.fetchone()

    if not atual:
        print("❌ ID não encontrado.")
        return

    print(f"\nEditando: {atual[0]}")
    print("(Pressione ENTER para manter o valor atual)")

    # Lógica: se o input for vazio, usa o que já está no banco (atual[x])
    nova_data = ler_data(f"Nova data [{atual[0]}]: ") or atual[0]
    nova_descricao = input(f"Nova descrição [{atual[1]}]: ") or atual[1]

    # Para números, precisamos de um cuidado extra
    novo_valor_str = input(f"Novo valor [{atual[2]}]: ")
    novo_valor = float(novo_valor_str.replace(",", ".")) if novo_valor_str else atual[2]

    novo_id_conta_str = input(f"Novo ID Conta [{atual[3]}]: ")
    novo_id_conta = (
        int(novo_id_conta_str.replace(",", ".")) if novo_id_conta_str else atual[3]
    )

    novo_id_categoria_str = input(f"Novo ID Categoria [{atual[4]}]: ")
    novo_id_categoria = (
        int(novo_id_categoria_str.replace(",", "."))
        if novo_id_categoria_str
        else atual[4]
    )

    banco.editar_transacao(
        id_alvo, nova_data, nova_descricao, novo_valor, novo_id_conta, novo_id_categoria
    )


def menu_total_gasto_por_categoria():
    banco.listar_nome_categorias()
    categoria = ler_str("Escolha a categoria: ")
    banco.total_gastos_por_categoria(categoria)

from classes import Categoria, Conta, GerenciadorFinancas, Transacao
from leitores import ler_data, ler_float, ler_str

banco = GerenciadorFinancas("receitas_despesas.db")


def menu_cadastrar_conta():
    nome_conta = ler_str("Instituição: ")
    moeda = ler_str("Moeda: (BRL / EUR)")
    saldo = ler_float("Saldo Inicial: ")
    tipo = ler_str("Tipo: ")

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


def menu_exibir_extrato():
    banco.exibir_extrato()


def menu_total_gasto_por_categoria():
    categoria = ler_str("Categoria: ")
    banco.total_gastos_por_categoria(categoria)

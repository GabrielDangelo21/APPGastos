import locale
from leitores import ler_str
from mostradores import (
    mostrar_menu,
    mostrar_menu_categorias,
    mostrar_menu_contas,
    mostrar_menu_transacoes,
)
from servicos import (
    menu_cadastrar_categoria,
    # menu_cadastrar_conta,
    menu_cadastrar_transacao,
    menu_editar_categoria,
    # menu_editar_conta,
    menu_editar_transacao,
    menu_excluir_transacao,
    menu_exibir_categorias,
    # menu_exibir_contas,
    menu_exibir_transacoes,
    menu_total_gasto_por_categoria,
)

# Tenta configurar para Português do Brasil (UTF-8 é o padrão moderno)
try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except locale.Error:
    # Caso o sistema não tenha o locale pt_BR (comum no Windows ou Docker),
    # ele usa a configuração padrão do sistema operacional do usuário.
    locale.setlocale(locale.LC_ALL, "")


def menu():

    while True:
        mostrar_menu()

        opcao = ler_str("Escolha uma opção: ")

        if opcao == "1":
            while True:
                mostrar_menu_categorias()
                opcao_categorias = ler_str("Escolha uma opção: ")
                if opcao_categorias == "1":
                    menu_cadastrar_categoria()
                elif opcao_categorias == "2":
                    menu_exibir_categorias()
                elif opcao_categorias == "3":
                    menu_editar_categoria()
                elif opcao_categorias == "4":
                    menu_total_gasto_por_categoria()
                elif opcao_categorias == "0":
                    print("Voltando ao menu principal...")
                    break

        elif opcao == "2":
            while True:
                mostrar_menu_transacoes()
                opcao_transacoes = ler_str("Escolha uma opção: ")
                if opcao_transacoes == "1":
                    menu_cadastrar_transacao()
                elif opcao_transacoes == "2":
                    menu_exibir_transacoes()
                elif opcao_transacoes == "3":
                    menu_editar_transacao()
                elif opcao_transacoes == "4":
                    menu_excluir_transacao()
                elif opcao_transacoes == "0":
                    print("Voltando ao menu principal...")
                    break

        elif opcao == "0":
            print("Encerrando o sistema. Até logo!")
            break


# O ponto de partida do programa
if __name__ == "__main__":
    menu()

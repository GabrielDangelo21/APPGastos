import locale
from leitores import ler_str
from mostradores import mostrar_menu
from servicos import (
    menu_cadastrar_categoria,
    menu_cadastrar_conta,
    menu_cadastrar_transacao,
    menu_editar_categoria,
    menu_editar_conta,
    menu_editar_transacao,
    menu_exibir_contas,
    menu_exibir_categoria,
    menu_exibir_transacao,
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
            menu_cadastrar_conta()

        elif opcao == "2":
            menu_cadastrar_categoria()

        elif opcao == "3":
            menu_cadastrar_transacao()

        elif opcao == "4":
            menu_exibir_contas()

        elif opcao == "5":
            menu_exibir_categoria()

        elif opcao == "6":
            menu_exibir_transacao()

        elif opcao == "7":
            menu_editar_conta()

        elif opcao == "8":
            menu_editar_categoria()

        elif opcao == "9":
            menu_editar_transacao()

        elif opcao == "10":
            menu_total_gasto_por_categoria()

        elif opcao == "0":
            print("Saindo...")
            break


# O ponto de partida do programa
if __name__ == "__main__":
    menu()

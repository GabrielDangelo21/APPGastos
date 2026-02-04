from datetime import date, datetime


def ler_data(prompt: str) -> date:
    while True:
        try:
            data_prompt = input(prompt)
            data_format = "%Y-%m-%d"
            data_convertida = datetime.strptime(data_prompt, data_format).date()

            # PEGA A DATA DE HOJE
            hoje = date.today()

            # VALIDAÇÃO: Se a data digitada for maior que hoje
            if data_convertida > hoje:
                print(
                    f"Erro: Não é permitido registrar transações futuras (Hoje é {hoje})."
                )
            else:
                return data_convertida

        except ValueError:
            print("Digite uma data válida no formato YYYY-MM-DD")


def ler_str(prompt: str) -> str:
    while True:
        valor = input(prompt)
        if valor.strip() != "":
            return valor
        print("Entrada vazia, digite algo.")


def ler_int(prompt: str) -> int:
    while True:
        try:
            valor = int(input(prompt))
            return valor
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")


def ler_float(prompt: str) -> float:
    while True:
        try:
            # Substituímos a vírgula por ponto para o Python não reclamar
            valor_texto = input(prompt).replace(",", ".")
            valor = float(valor_texto)
            if valor <= 0:
                print("Erro: O valor deve ser maior que zero.")
            else:
                return valor
        except ValueError:
            print("Entrada inválida. Digite um valor numérico (ex: 10.50).")

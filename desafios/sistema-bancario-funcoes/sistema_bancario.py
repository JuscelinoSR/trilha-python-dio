"""Sistema bancário didático, executado no terminal e sem persistência."""

from decimal import Decimal, InvalidOperation
import re


CENTAVOS = Decimal("0.01")
LIMITE_SAQUE = Decimal("500.00")
LIMITE_SAQUES = 3
MENU = """
Sistema bancário
[d] Depositar
[s] Sacar
[e] Exibir extrato
[q] Sair
Escolha uma opção: """


def formatar_reais(valor: Decimal) -> str:
    """Formata valores apenas na apresentação; os cálculos usam Decimal."""
    return "R$ " + f"{valor:,.2f}".translate(str.maketrans({",": ".", ".": ","}))


def ler_valor(texto: str) -> Decimal:
    """Converte valores com vírgula ou ponto, sem separadores de milhar."""
    texto = texto.strip()
    if not re.fullmatch(r"-?[0-9]+(?:[.,][0-9]{1,2})?", texto):
        raise ValueError("Digite um número com até duas casas decimais, como 100,50.")
    try:
        return Decimal(texto.replace(",", ".")).quantize(CENTAVOS)
    except InvalidOperation as erro:
        raise ValueError("O valor informado excede a precisão deste simulador.") from erro


def validar_valor(valor: Decimal) -> None:
    """Exige valor monetário positivo, finito e com precisão de centavos."""
    if not isinstance(valor, Decimal) or not valor.is_finite():
        raise ValueError("Informe um valor monetário válido.")
    if valor <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    try:
        arredondado = valor.quantize(CENTAVOS)
    except InvalidOperation as erro:
        raise ValueError("O valor informado excede a precisão deste simulador.") from erro
    if arredondado != valor:
        raise ValueError("Use no máximo duas casas decimais.")


def depositar(saldo: Decimal, valor: Decimal, extrato: str, /) -> tuple[Decimal, str]:
    """Retorna o novo saldo e o histórico. Os argumentos são posicionais."""
    validar_valor(valor)
    novo_saldo = saldo + valor
    novo_extrato = extrato + f"Depósito: {formatar_reais(valor)}\n"
    return novo_saldo, novo_extrato


def sacar(
    *,
    saldo: Decimal,
    valor: Decimal,
    extrato: str,
    limite: Decimal,
    numero_saques: int,
    limite_saques: int,
) -> tuple[Decimal, str, int]:
    """Retorna saldo, histórico e contador. Os argumentos são nomeados."""
    validar_valor(valor)
    if valor > saldo:
        raise ValueError("Saldo insuficiente.")
    if valor > limite:
        raise ValueError(f"O limite por saque é {formatar_reais(limite)}.")
    if numero_saques >= limite_saques:
        raise ValueError(f"O limite de {limite_saques} saques por execução foi atingido.")
    novo_saldo = saldo - valor
    novo_extrato = extrato + f"Saque: {formatar_reais(valor)}\n"
    return novo_saldo, novo_extrato, numero_saques + 1


def gerar_extrato(saldo: Decimal, /, *, extrato: str) -> str:
    """Recebe saldo por posição e histórico por nome; não altera o estado."""
    historico = extrato.rstrip() if extrato else "Nenhuma movimentação registrada."
    return f"\nEXTRATO\n{historico}\nSaldo atual: {formatar_reais(saldo)}\n"


def main() -> None:
    """Cuida da interação e aplica os estados retornados pelas operações."""
    saldo = Decimal("0.00")
    extrato = ""
    numero_saques = 0
    print("Simulador educacional. Saldo e histórico são reiniciados ao sair.")
    print(f"Até {LIMITE_SAQUES} saques por execução, de até {formatar_reais(LIMITE_SAQUE)} cada.")
    while True:
        try:
            opcao = input(MENU).strip().lower()
            if opcao == "q":
                print("Sessão encerrada.")
                break
            if opcao == "e":
                print(gerar_extrato(saldo, extrato=extrato))
            elif opcao in {"d", "s"}:
                valor = ler_valor(input("Valor (ex.: 100,50, sem separador de milhar): "))
                if opcao == "d":
                    saldo, extrato = depositar(saldo, valor, extrato)
                    print("Depósito realizado.")
                else:
                    saldo, extrato, numero_saques = sacar(
                        saldo=saldo,
                        valor=valor,
                        extrato=extrato,
                        limite=LIMITE_SAQUE,
                        numero_saques=numero_saques,
                        limite_saques=LIMITE_SAQUES,
                    )
                    print("Saque realizado.")
            else:
                print("Opção inválida. Use d, s, e ou q.")
        except ValueError as erro:
            print(f"Operação não realizada: {erro}")
        except (EOFError, KeyboardInterrupt):
            print("\nSessão encerrada.")
            break


if __name__ == "__main__":
    main()

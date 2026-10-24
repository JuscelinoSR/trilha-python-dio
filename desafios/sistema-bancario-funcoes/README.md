# Sistema bancário com funções em Python

Projeto educacional baseado no desafio da DIO: organizar as operações de depósito, saque e extrato em funções reutilizáveis. A interação fica no terminal e as regras de negócio ficam separadas da leitura dos dados.

Esta solução complementa os exemplos de `00 - Fundamentos/desafio.py` e `01 - Estrutura de dados/desafio.py`, preservados nas pastas das aulas. O foco é demonstrar depósito, saque e extrato com regras testáveis e controle correto do estado.

A versão de Estrutura de dados incrementa `numero_saques` dentro de `sacar`, mas retorna apenas saldo e extrato. Como inteiros não são alterados no chamador por essa atribuição local, o contador do menu permanece igual. Aqui, a função retorna também o contador atualizado e o menu aplica os três valores. O teste de terceiro e quarto saques verifica essa regra.

## Funcionalidades

- Depósitos de valores positivos.
- Saques sujeitos ao saldo, ao limite por operação e à quantidade permitida.
- Histórico de depósitos e saques, com saldo atualizado.
- Mensagens para entradas inválidas, saldo insuficiente e limites atingidos.
- Valores monetários tratados com `Decimal`, evitando imprecisões de ponto flutuante binário.

## Regras adotadas

Este projeto mantém os limites de R$ 500 por saque e três saques por execução presentes nos exemplos do repositório. As constantes estão no início de `sistema_bancario.py` e podem ser ajustadas.

| Regra | Comportamento |
| --- | --- |
| Depósito | Valor finito, positivo e com precisão de centavos |
| Saque | Mesmas condições do depósito, saldo suficiente e limite de R$ 500 |
| Quantidade de saques | Até três operações aprovadas por execução |
| Operação recusada | Não altera saldo, histórico nem contador |
| Extrato | Mostra a sequência das operações e o saldo atual |
| Sem movimentação | Exibe uma mensagem específica e saldo zero |
| Encerramento | Os dados em memória são descartados |

O limite é **por execução**, pois esta versão não tem controle de data ou armazenamento persistente. Reiniciar o programa reinicia saldo, histórico e contador.

## Como executar

Requisito: **Python 3.10 ou superior**. Não há dependências externas.

Na raiz deste repositório, entre na pasta da solução:

```bash
cd desafios/sistema-bancario-funcoes
```

Depois execute:

```bash
python sistema_bancario.py
```

No Windows, se `python` não estiver configurado, use:

```powershell
py sistema_bancario.py
```

| Opção | Ação |
| --- | --- |
| `d` | Depositar |
| `s` | Sacar |
| `e` | Exibir extrato |
| `q` | Encerrar |

Digite valores como `100`, `100,50` ou `100.50`, sem separadores de milhar. O programa aceita vírgula ou ponto como separador decimal, com até duas casas. Não aceita expressões, notação científica ou valores não finitos.

## Organização das funções

### `depositar(saldo, valor, extrato, /)`

Recebe os argumentos somente por posição. Valida o valor e retorna o novo saldo e o histórico atualizado.

```python
saldo, historico = depositar(saldo, Decimal("100.50"), historico)
```

O `/` impede chamadas como `depositar(saldo=..., valor=..., extrato=...)`. Isso demonstra parâmetros posicionais exclusivos.

### `sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques)`

Recebe os argumentos somente pelo nome, pois há vários valores com significados diferentes. Retorna novo saldo, histórico e contador de saques aprovados.

```python
saldo, historico, numero_saques = sacar(
    saldo=saldo,
    valor=Decimal("50.00"),
    extrato=historico,
    limite=LIMITE_SAQUE,
    numero_saques=numero_saques,
    limite_saques=LIMITE_SAQUES,
)
```

O `*` obriga a nomear cada argumento. A validação ocorre antes da construção do novo estado. Se houver erro, a função lança `ValueError` e não retorna um estado alterado.

### `gerar_extrato(saldo, /, *, extrato)`

Combina os dois estilos: saldo por posição e histórico pelo nome. Retorna o texto do extrato sem modificar os dados. O `main()` é responsável por exibir esse texto.

```python
print(gerar_extrato(saldo, extrato=historico))
```

### Funções auxiliares

| Função | Responsabilidade |
| --- | --- |
| `ler_valor` | Converte texto do terminal para `Decimal` |
| `validar_valor` | Verifica se o valor pode ser movimentado |
| `formatar_reais` | Apresenta os valores no formato brasileiro |
| `main` | Mostra o menu, lê os dados e aplica os resultados das operações |

As funções de operação não usam `input()` ou `print()`. Assim, podem ser testadas ou chamadas por outra interface. Importar o módulo também não inicia o menu, graças à condição `if __name__ == "__main__"`.

## Exemplo de utilização

1. Deposite R$ 100,50.
2. Saque R$ 25,25.
3. Selecione `e` para consultar.

O resultado esperado é:

```text
EXTRATO
Depósito: R$ 100,50
Saque: R$ 25,25
Saldo atual: R$ 75,25
```

## Testes

Os testes usam `unittest`, da biblioteca padrão:

```bash
python -m unittest -v
```

A suíte verifica depósitos, saques nos limites, saldo insuficiente, terceiro e quarto saques, entradas inválidas, precisão de centavos, preservação do histórico e contratos dos parâmetros. Também executa o programa pelo terminal para testar uma entrada incorreta seguida de operações válidas.

O fluxo principal conferido recebe `abc` e mantém o programa aberto, deposita R$ 100,50, saca R$ 25,25 e apresenta saldo de R$ 75,25.

## Estrutura

```text
sistema_bancario.py
test_sistema_bancario.py
README.md
DESCRICAO.md
evidencias/
  testes.txt
  exemplo-terminal.txt
```

Os arquivos de evidência registram uma execução dos testes e do exemplo, sem dados pessoais ou bancários reais.

## Conceitos demonstrados

- Funções com responsabilidades definidas.
- Parâmetros posicionais, nomeados e combinação dos dois.
- Retorno de múltiplos valores em tuplas.
- Separação entre regras de negócio e interação com o usuário.
- Tratamento de exceções e preservação do estado após falhas.
- Uso de `Decimal` para valores monetários.
- Anotações de tipos e testes automatizados.

## Limites da versão

O programa simula uma única conta em memória. Não tem autenticação, cadastro de clientes, banco de dados, persistência, integração bancária ou controle de limite por dia. É uma ferramenta de estudo e não deve movimentar dinheiro real.

## Entrega na DIO

Repositório: [JuscelinoSR/trilha-python-dio](https://github.com/JuscelinoSR/trilha-python-dio).

Use o endereço do repositório no botão **Entregar Projeto** e indique a pasta `desafios/sistema-bancario-funcoes`. A breve descrição está em `DESCRICAO.md`.

Referências: descrição do desafio da DIO fornecida pelo usuário e exemplos bancários das pastas Fundamentos e Estrutura de dados. Os arquivos das aulas permanecem preservados. Cadastro de usuários e contas, existente no exemplo de Estrutura de dados, não faz parte desta solução focada nas três operações solicitadas.

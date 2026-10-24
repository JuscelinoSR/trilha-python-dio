"""Verifica as regras de negócio, os contratos das funções e o uso pelo terminal."""

from decimal import Decimal
import os
import subprocess
import sys
import unittest
from pathlib import Path

from sistema_bancario import depositar, formatar_reais, gerar_extrato, ler_valor, sacar


class SistemaBancarioTests(unittest.TestCase):
    def sacar(self, **alteracoes):
        parametros = dict(
            saldo=Decimal("1000.00"),
            valor=Decimal("100.00"),
            extrato="",
            limite=Decimal("500.00"),
            numero_saques=0,
            limite_saques=3,
        )
        parametros.update(alteracoes)
        return sacar(**parametros)

    def test_deposito_atualiza_saldo_e_historico(self):
        saldo, historico = depositar(Decimal("10.00"), Decimal("25.50"), "")
        self.assertEqual(saldo, Decimal("35.50"))
        self.assertEqual(historico, "Depósito: R$ 25,50\n")

    def test_deposito_rejeita_valores_invalidos_sem_mudar_estado(self):
        saldo, historico = Decimal("50.00"), "histórico anterior\n"
        for valor in [Decimal("0"), Decimal("-1"), Decimal("NaN"), Decimal("Infinity"), Decimal("1.001")]:
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                depositar(saldo, valor, historico)
        self.assertEqual(saldo, Decimal("50.00"))
        self.assertEqual(historico, "histórico anterior\n")

    def test_saque_exatamente_no_limite(self):
        saldo, historico, contador = self.sacar(valor=Decimal("500.00"))
        self.assertEqual((saldo, contador), (Decimal("500.00"), 1))
        self.assertEqual(historico, "Saque: R$ 500,00\n")

    def test_saque_pode_zerar_saldo(self):
        saldo, _, contador = self.sacar(saldo=Decimal("100"), valor=Decimal("100"))
        self.assertEqual(saldo, Decimal("0"))
        self.assertEqual(contador, 1)

    def test_saque_rejeita_saldo_insuficiente(self):
        with self.assertRaisesRegex(ValueError, "Saldo insuficiente"):
            self.sacar(saldo=Decimal("99.99"))

    def test_saque_rejeita_um_centavo_acima_do_limite(self):
        with self.assertRaisesRegex(ValueError, "limite por saque"):
            self.sacar(valor=Decimal("500.01"))

    def test_terceiro_saque_permitido_e_quarto_bloqueado(self):
        saldo, historico, contador = self.sacar(numero_saques=2)
        self.assertEqual(contador, 3)
        with self.assertRaisesRegex(ValueError, "3 saques"):
            self.sacar(saldo=saldo, extrato=historico, numero_saques=contador)
        self.assertEqual(saldo, Decimal("900.00"))
        self.assertEqual(historico.count("Saque:"), 1)

    def test_saque_rejeita_zero_negativo_e_nao_finito(self):
        for valor in [Decimal("0"), Decimal("-0.01"), Decimal("NaN"), Decimal("Infinity")]:
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                self.sacar(valor=valor)

    def test_extrato_vazio(self):
        resultado = gerar_extrato(Decimal("0.00"), extrato="")
        self.assertIn("Nenhuma movimentação registrada.", resultado)
        self.assertIn("Saldo atual: R$ 0,00", resultado)

    def test_fluxo_completo_preserva_ordem_e_centavos(self):
        saldo, historico = depositar(Decimal("0.00"), Decimal("100.10"), "")
        saldo, historico = depositar(saldo, Decimal("0.20"), historico)
        saldo, historico, contador = self.sacar(
            saldo=saldo, extrato=historico, valor=Decimal("25.30")
        )
        self.assertEqual(saldo, Decimal("75.00"))
        self.assertEqual(contador, 1)
        self.assertEqual(historico.splitlines(), [
            "Depósito: R$ 100,10", "Depósito: R$ 0,20", "Saque: R$ 25,30"
        ])
        self.assertIn("Saldo atual: R$ 75,00", gerar_extrato(saldo, extrato=historico))

    def test_entrada_aceita_virgula_ponto_e_espacos(self):
        self.assertEqual(ler_valor(" 100,50 "), Decimal("100.50"))
        self.assertEqual(ler_valor("100.50"), Decimal("100.50"))

    def test_entrada_rejeita_texto_milhar_e_precisao_excessiva(self):
        for texto in ["", "abc", "NaN", "inf", "1e3", "1.000,00", "1,001", "10.005"]:
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                ler_valor(texto)

    def test_contratos_posicionais_e_nomeados(self):
        with self.assertRaises(TypeError):
            depositar(saldo=Decimal("0"), valor=Decimal("10"), extrato="")
        with self.assertRaises(TypeError):
            sacar(Decimal("100"), Decimal("10"), "", Decimal("500"), 0, 3)
        with self.assertRaises(TypeError):
            gerar_extrato(Decimal("0"), "")

    def test_formatacao_brasileira(self):
        self.assertEqual(formatar_reais(Decimal("1234.56")), "R$ 1.234,56")

    def test_terminal_se_recupera_de_entrada_invalida(self):
        script = Path(__file__).with_name("sistema_bancario.py")
        resultado = subprocess.run(
            [sys.executable, str(script)],
            input="d\nabc\nd\n100,50\ns\n25,25\ne\nq\n",
            text=True, encoding="utf-8", capture_output=True,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            check=True,
        )
        self.assertIn("Operação não realizada", resultado.stdout)
        self.assertIn("Saldo atual: R$ 75,25", resultado.stdout)
        self.assertIn("Sessão encerrada.", resultado.stdout)


if __name__ == "__main__":
    unittest.main()

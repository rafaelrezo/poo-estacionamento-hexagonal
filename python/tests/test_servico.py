"""Os casos de uso são testados com adaptadores leves: repositório em memória e
relógio simulado. Nenhum arquivo, terminal ou banco é necessário."""

import unittest

from estacionamento.adaptadores.saida.relogios import RelogioSimulado
from estacionamento.adaptadores.saida.repositorio_memoria import RepositorioMemoria
from estacionamento.aplicacao.servico import ServicoEstacionamento
from estacionamento.dominio.erros import ErroEstacionamento
from estacionamento.dominio.tarifa import TarifaFixa, TarifaPorHora


class TestServicoEstacionamento(unittest.TestCase):
    def setUp(self):
        self.relogio = RelogioSimulado(480)
        self.servico = ServicoEstacionamento(
            2, TarifaPorHora(800, 15), RepositorioMemoria(), self.relogio)

    def test_entrada_ocupa_vaga(self):
        self.servico.registrar_entrada("ABC1D23")
        self.assertEqual(self.servico.vagas_livres(), 1)

    def test_mesma_placa_nao_entra_duas_vezes(self):
        self.servico.registrar_entrada("ABC1D23")
        with self.assertRaisesRegex(ErroEstacionamento, "ABC1D23 já está no pátio"):
            self.servico.registrar_entrada("abc-1d23")

    def test_patio_lotado(self):
        self.servico.registrar_entrada("ABC1D23")
        self.servico.registrar_entrada("XYZ9876")
        with self.assertRaisesRegex(ErroEstacionamento, "pátio lotado"):
            self.servico.registrar_entrada("QWE1R23")

    def test_saida_sem_entrada(self):
        with self.assertRaisesRegex(ErroEstacionamento, "não há entrada aberta para QWE1R23"):
            self.servico.registrar_saida("QWE1R23")

    def test_saida_cobra_e_libera_vaga(self):
        self.servico.registrar_entrada("ABC1D23")
        self.relogio.avancar(95)
        recibo = self.servico.registrar_saida("ABC1D23")
        self.assertEqual((recibo.permanencia, recibo.valor_centavos), (95, 1600))
        self.assertEqual(self.servico.vagas_livres(), 2)

    def test_reentrada_cria_novo_ticket(self):
        self.servico.registrar_entrada("ABC1D23")
        self.servico.registrar_saida("ABC1D23")
        self.servico.registrar_entrada("ABC1D23")
        self.assertEqual(len(self.servico.historico()), 2)

    def test_capacidade_zero_e_recusada(self):
        with self.assertRaisesRegex(ErroEstacionamento, "capacidade deve ser positiva"):
            ServicoEstacionamento(0, TarifaFixa(2000), RepositorioMemoria(), self.relogio)

    def test_trocar_estrategia_nao_muda_o_servico(self):
        evento = ServicoEstacionamento(10, TarifaFixa(2000), RepositorioMemoria(), self.relogio)
        evento.registrar_entrada("ABC1234")
        self.relogio.avancar(5)
        self.assertEqual(evento.registrar_saida("ABC1234").valor_centavos, 2000)


if __name__ == "__main__":
    unittest.main()

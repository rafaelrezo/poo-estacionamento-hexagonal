"""O domínio é testado sem portas nem adaptadores: só objetos e valores."""

import unittest

from estacionamento.dominio.erros import ErroEstacionamento
from estacionamento.dominio.placa import Placa
from estacionamento.dominio.tarifa import TarifaFixa, TarifaPorHora
from estacionamento.dominio.ticket import Ticket


class TestPlaca(unittest.TestCase):
    def test_normaliza_mercosul(self):
        self.assertEqual(Placa("abc-1d23").texto, "ABC1D23")

    def test_aceita_formato_antigo(self):
        self.assertEqual(Placa("ABC1234").texto, "ABC1234")

    def test_recusa_formatos_invalidos(self):
        for texto in ["AB12345", "ABCD123", ""]:
            with self.subTest(texto=texto):
                with self.assertRaisesRegex(ErroEstacionamento, "placa inválida"):
                    Placa(texto)


class TestTarifas(unittest.TestCase):
    def test_tarifa_por_hora_nas_fronteiras(self):
        tarifa = TarifaPorHora(800, 15)
        casos = {15: 0, 16: 800, 60: 800, 61: 1600, 95: 1600}
        for minutos, esperado in casos.items():
            with self.subTest(minutos=minutos):
                self.assertEqual(tarifa.calcular(minutos), esperado)

    def test_recusa_permanencia_negativa(self):
        with self.assertRaisesRegex(ErroEstacionamento, "permanência negativa"):
            TarifaPorHora(800, 15).calcular(-1)

    def test_tarifa_fixa_nao_depende_do_tempo(self):
        self.assertEqual(TarifaFixa(2000).calcular(300), 2000)


class TestTicket(unittest.TestCase):
    def setUp(self):
        self.tarifa = TarifaPorHora(800, 15)
        self.ticket = Ticket(Placa("ABC1D23"), 480)

    def test_ticket_novo_esta_aberto(self):
        self.assertTrue(self.ticket.aberto)
        self.assertIsNone(self.ticket.permanencia)

    def test_saida_antes_da_entrada_mantem_ticket_aberto(self):
        with self.assertRaisesRegex(ErroEstacionamento, "anterior à entrada"):
            self.ticket.fechar(479, self.tarifa)
        self.assertTrue(self.ticket.aberto)

    def test_fechar_calcula_permanencia_e_valor(self):
        self.ticket.fechar(575, self.tarifa)
        self.assertEqual((self.ticket.permanencia, self.ticket.valor_centavos), (95, 1600))

    def test_nao_fecha_duas_vezes(self):
        self.ticket.fechar(575, self.tarifa)
        with self.assertRaisesRegex(ErroEstacionamento, "já foi fechado"):
            self.ticket.fechar(600, self.tarifa)

    def test_restauracao_incoerente_e_recusada(self):
        with self.assertRaisesRegex(ErroEstacionamento, "coerentes"):
            Ticket.restaurar(Placa("ABC1D23"), 480, 500, None)


if __name__ == "__main__":
    unittest.main()

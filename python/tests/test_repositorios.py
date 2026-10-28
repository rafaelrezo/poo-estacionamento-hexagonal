"""Teste de contrato: as mesmas verificações valem para qualquer adaptador da
porta RepositorioTickets. Um adaptador novo deve passar por elas."""

import os
import tempfile
import unittest

from estacionamento.adaptadores.saida.repositorio_memoria import RepositorioMemoria
from estacionamento.adaptadores.saida.repositorio_sqlite import RepositorioSQLite
from estacionamento.dominio.placa import Placa
from estacionamento.dominio.tarifa import TarifaPorHora
from estacionamento.dominio.ticket import Ticket


class ContratoRepositorio:
    """Mixin: cada subclasse informa como criar o adaptador a verificar."""

    def criar_repositorio(self):
        raise NotImplementedError

    def setUp(self):
        self.repositorio = self.criar_repositorio()
        self.placa = Placa("ABC1D23")
        self.tarifa = TarifaPorHora(800, 15)

    def test_comeca_vazio(self):
        self.assertEqual(self.repositorio.contar_abertos(), 0)
        self.assertIsNone(self.repositorio.buscar_aberto(self.placa))

    def test_encontra_ticket_aberto(self):
        self.repositorio.salvar(Ticket(self.placa, 480))
        self.assertIsNotNone(self.repositorio.buscar_aberto(self.placa))
        self.assertEqual(self.repositorio.contar_abertos(), 1)

    def test_fechar_substitui_sem_duplicar(self):
        self.repositorio.salvar(Ticket(self.placa, 480))
        ticket = self.repositorio.buscar_aberto(self.placa)
        ticket.fechar(575, self.tarifa)
        self.repositorio.salvar(ticket)
        self.assertIsNone(self.repositorio.buscar_aberto(self.placa))
        self.assertEqual(len(self.repositorio.listar()), 1)

    def test_alterar_ticket_buscado_nao_altera_registro_antes_de_salvar(self):
        self.repositorio.salvar(Ticket(self.placa, 480))
        self.repositorio.buscar_aberto(self.placa).fechar(575, self.tarifa)
        self.assertEqual(self.repositorio.contar_abertos(), 1)

    def test_reentrada_no_mesmo_minuto_cria_outro_registro(self):
        self.repositorio.salvar(Ticket(self.placa, 480))
        ticket = self.repositorio.buscar_aberto(self.placa)
        ticket.fechar(575, self.tarifa)
        self.repositorio.salvar(ticket)
        self.repositorio.salvar(Ticket(self.placa, 575))
        self.assertEqual(len(self.repositorio.listar()), 2)
        self.assertEqual(self.repositorio.contar_abertos(), 1)


class TestRepositorioMemoria(ContratoRepositorio, unittest.TestCase):
    def criar_repositorio(self):
        return RepositorioMemoria()


class TestRepositorioSQLite(ContratoRepositorio, unittest.TestCase):
    def criar_repositorio(self):
        repositorio = RepositorioSQLite(":memory:")
        self.addCleanup(repositorio.fechar_conexao)
        return repositorio

    def test_dados_sobrevivem_a_nova_conexao(self):
        pasta = tempfile.mkdtemp()
        caminho = os.path.join(pasta, "historico.db")
        primeiro = RepositorioSQLite(caminho)
        primeiro.salvar(Ticket(self.placa, 480))
        primeiro.fechar_conexao()
        segundo = RepositorioSQLite(caminho)
        self.addCleanup(segundo.fechar_conexao)
        self.assertEqual(segundo.contar_abertos(), 1)


if __name__ == "__main__":
    unittest.main()

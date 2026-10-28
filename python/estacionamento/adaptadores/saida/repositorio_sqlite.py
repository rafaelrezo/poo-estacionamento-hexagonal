import sqlite3
from typing import List, Optional

from estacionamento.aplicacao.portas import RepositorioTickets
from estacionamento.dominio.placa import Placa
from estacionamento.dominio.ticket import Ticket


class RepositorioSQLite(RepositorioTickets):
    """Mesma porta, outra tecnologia. O SQL fica aqui; o núcleo não o conhece."""

    def __init__(self, caminho: str):
        self._conexao = sqlite3.connect(caminho)
        with self._conexao:
            self._conexao.execute(
                "CREATE TABLE IF NOT EXISTS tickets ("
                " placa TEXT NOT NULL,"
                " entrada INTEGER NOT NULL,"
                " saida INTEGER,"
                " valor_centavos INTEGER)"
            )

    def fechar_conexao(self) -> None:
        self._conexao.close()

    def salvar(self, ticket: Ticket) -> None:
        with self._conexao:  # transação: confirma ao sair ou desfaz em caso de erro
            cursor = self._conexao.execute(
                "UPDATE tickets SET entrada = ?, saida = ?, valor_centavos = ?"
                " WHERE placa = ? AND saida IS NULL",
                (ticket.entrada, ticket.saida, ticket.valor_centavos, ticket.placa.texto),
            )
            if cursor.rowcount == 0:
                self._conexao.execute(
                    "INSERT INTO tickets (placa, entrada, saida, valor_centavos)"
                    " VALUES (?, ?, ?, ?)",
                    (ticket.placa.texto, ticket.entrada, ticket.saida, ticket.valor_centavos),
                )

    def buscar_aberto(self, placa: Placa) -> Optional[Ticket]:
        linha = self._conexao.execute(
            "SELECT placa, entrada, saida, valor_centavos FROM tickets"
            " WHERE placa = ? AND saida IS NULL",
            (placa.texto,),
        ).fetchone()
        return None if linha is None else self._restaurar(linha)

    def contar_abertos(self) -> int:
        return self._conexao.execute(
            "SELECT COUNT(*) FROM tickets WHERE saida IS NULL"
        ).fetchone()[0]

    def listar(self) -> List[Ticket]:
        linhas = self._conexao.execute(
            "SELECT placa, entrada, saida, valor_centavos FROM tickets ORDER BY rowid"
        ).fetchall()
        return [self._restaurar(linha) for linha in linhas]

    @staticmethod
    def _restaurar(linha) -> Ticket:
        placa, entrada, saida, valor = linha
        return Ticket.restaurar(Placa(placa), entrada, saida, valor)

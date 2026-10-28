import copy
from typing import List, Optional

from estacionamento.aplicacao.portas import RepositorioTickets
from estacionamento.dominio.placa import Placa
from estacionamento.dominio.ticket import Ticket


class RepositorioMemoria(RepositorioTickets):
    """Adaptador mais simples da porta: útil em testes e demonstrações.

    Guarda e devolve cópias. Assim, alterar um ticket buscado não altera o
    registro antes de `salvar`, como aconteceria com um banco real."""

    def __init__(self):
        self._tickets: List[Ticket] = []

    def salvar(self, ticket: Ticket) -> None:
        for indice, existente in enumerate(self._tickets):
            if existente.aberto and existente.placa == ticket.placa:
                self._tickets[indice] = copy.copy(ticket)
                return
        self._tickets.append(copy.copy(ticket))

    def buscar_aberto(self, placa: Placa) -> Optional[Ticket]:
        for ticket in self._tickets:
            if ticket.aberto and ticket.placa == placa:
                return copy.copy(ticket)
        return None

    def contar_abertos(self) -> int:
        return sum(1 for ticket in self._tickets if ticket.aberto)

    def listar(self) -> List[Ticket]:
        return [copy.copy(ticket) for ticket in self._tickets]

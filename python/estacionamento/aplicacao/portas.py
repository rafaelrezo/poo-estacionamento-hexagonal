"""Portas de saída: o que o núcleo precisa do mundo externo, descrito nos termos
do próprio núcleo. Quem implementa são os adaptadores; quem escolhe é a montagem."""

from abc import ABC, abstractmethod
from typing import List, Optional

from estacionamento.dominio.placa import Placa
from estacionamento.dominio.ticket import Ticket


class RepositorioTickets(ABC):
    @abstractmethod
    def salvar(self, ticket: Ticket) -> None:
        """Substitui o ticket aberto da mesma placa ou, se não houver, acrescenta."""

    @abstractmethod
    def buscar_aberto(self, placa: Placa) -> Optional[Ticket]:
        """Devolve o ticket aberto da placa, se houver."""

    @abstractmethod
    def contar_abertos(self) -> int:
        """Quantidade de veículos no pátio."""

    @abstractmethod
    def listar(self) -> List[Ticket]:
        """Todos os tickets, na ordem de entrada."""


class Relogio(ABC):
    @abstractmethod
    def agora_em_minutos(self) -> int:
        """Instante atual em minutos."""

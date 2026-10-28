from typing import List

from estacionamento.aplicacao.portas import Relogio, RepositorioTickets
from estacionamento.dominio.erros import ErroEstacionamento
from estacionamento.dominio.placa import Placa
from estacionamento.dominio.tarifa import Tarifa
from estacionamento.dominio.ticket import Ticket


class ServicoEstacionamento:
    """Porta de entrada: as operações públicas deste serviço são os casos de uso.
    Ele coordena domínio e portas; não lê teclado, não escreve arquivo."""

    def __init__(self, capacidade: int, tarifa: Tarifa,
                 repositorio: RepositorioTickets, relogio: Relogio):
        if capacidade <= 0:
            raise ErroEstacionamento("capacidade deve ser positiva")
        self._capacidade = capacidade
        self._tarifa = tarifa
        self._repositorio = repositorio
        self._relogio = relogio

    @property
    def capacidade(self) -> int:
        return self._capacidade

    def registrar_entrada(self, texto: str) -> Ticket:
        placa = Placa(texto)
        if self._repositorio.buscar_aberto(placa) is not None:
            raise ErroEstacionamento(f"{placa.texto} já está no pátio")
        if self.vagas_livres() == 0:
            raise ErroEstacionamento("pátio lotado")
        ticket = Ticket(placa, self._relogio.agora_em_minutos())
        self._repositorio.salvar(ticket)
        return ticket

    def registrar_saida(self, texto: str) -> Ticket:
        placa = Placa(texto)
        ticket = self._repositorio.buscar_aberto(placa)
        if ticket is None:
            raise ErroEstacionamento(f"não há entrada aberta para {placa.texto}")
        ticket.fechar(self._relogio.agora_em_minutos(), self._tarifa)
        self._repositorio.salvar(ticket)
        return ticket

    def vagas_livres(self) -> int:
        return self._capacidade - self._repositorio.contar_abertos()

    def historico(self) -> List[Ticket]:
        return self._repositorio.listar()

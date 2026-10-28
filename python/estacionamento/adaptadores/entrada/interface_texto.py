from typing import Optional, TextIO

from estacionamento.adaptadores.saida.relogios import RelogioSimulado
from estacionamento.aplicacao.servico import ServicoEstacionamento
from estacionamento.dominio.erros import ErroEstacionamento


class ErroComando(Exception):
    """Erro de uso do comando: pertence a este adaptador, não ao domínio."""


def formatar_horario(minutos: int) -> str:
    do_dia = minutos % (24 * 60)
    return f"{do_dia // 60:02d}:{do_dia % 60:02d}"


def formatar_reais(centavos: int) -> str:
    return f"R$ {centavos // 100},{centavos % 100:02d}"


def ler_minutos(texto: str) -> int:
    if not (texto.isascii() and texto.isdigit()) or len(texto) > 6:
        raise ErroComando("avancar exige minutos inteiros não negativos")
    return int(texto)


def exigir(argumento: str, uso: str) -> None:
    if not argumento:
        raise ErroComando(f"uso: {uso}")


class InterfaceTexto:
    """Adaptador de entrada: traduz linhas de texto em chamadas aos casos de uso e
    traduz os resultados em mensagens. Formatar dinheiro e horário é papel dele.

    `relogio_simulado` pode ser None; nesse caso o comando "avancar" é recusado."""

    def __init__(self, servico: ServicoEstacionamento,
                 relogio_simulado: Optional[RelogioSimulado]):
        self._servico = servico
        self._relogio_simulado = relogio_simulado

    def executar(self, entrada: TextIO, saida: TextIO) -> None:
        for linha in entrada:
            partes = linha.split()
            if not partes or partes[0].startswith("#"):
                continue
            comando = partes[0]
            argumento = partes[1] if len(partes) > 1 else ""
            if comando == "sair":
                break
            try:
                self._tratar(comando, argumento, saida)
            except (ErroEstacionamento, ErroComando) as erro:
                print(f"erro: {erro}", file=saida)

    def _tratar(self, comando: str, argumento: str, saida: TextIO) -> None:
        if comando == "entrada":
            exigir(argumento, "entrada PLACA")
            ticket = self._servico.registrar_entrada(argumento)
            print(f"entrada registrada: {ticket.placa.texto} às "
                  f"{formatar_horario(ticket.entrada)} "
                  f"(vagas livres: {self._servico.vagas_livres()})", file=saida)
        elif comando == "saida":
            exigir(argumento, "saida PLACA")
            ticket = self._servico.registrar_saida(argumento)
            print(f"saída registrada: {ticket.placa.texto} | {ticket.permanencia} min | "
                  f"{formatar_reais(ticket.valor_centavos)}", file=saida)
        elif comando == "avancar":
            if self._relogio_simulado is None:
                raise ErroComando("o relógio do sistema não pode ser avançado")
            self._relogio_simulado.avancar(ler_minutos(argumento))
            agora = self._relogio_simulado.agora_em_minutos()
            print(f"relógio: {formatar_horario(agora)}", file=saida)
        elif comando == "vagas":
            print(f"vagas livres: {self._servico.vagas_livres()} de "
                  f"{self._servico.capacidade}", file=saida)
        elif comando == "historico":
            tickets = self._servico.historico()
            if not tickets:
                print("histórico vazio", file=saida)
            for ticket in tickets:
                inicio = f"{ticket.placa.texto} | {formatar_horario(ticket.entrada)} -> "
                if ticket.aberto:
                    print(inicio + "no pátio", file=saida)
                else:
                    print(inicio + f"{formatar_horario(ticket.saida)} | "
                          f"{ticket.permanencia} min | "
                          f"{formatar_reais(ticket.valor_centavos)}", file=saida)
        elif comando == "ajuda":
            print("comandos: entrada PLACA, saida PLACA, avancar MINUTOS, vagas, historico, "
                  "ajuda, sair", file=saida)
        else:
            raise ErroComando(f"comando desconhecido: {comando} (digite ajuda)")

import time

from estacionamento.aplicacao.portas import Relogio


class RelogioSistema(Relogio):
    """Minutos desde 1970-01-01 em UTC, lidos do relógio do computador."""

    def agora_em_minutos(self) -> int:
        return int(time.time() // 60)


class RelogioSimulado(Relogio):
    """Relógio controlado: torna demonstrações e testes reproduzíveis."""

    def __init__(self, inicio: int):
        if inicio < 0:
            raise ValueError("relógio simulado não pode começar antes de zero")
        self._agora = inicio

    def agora_em_minutos(self) -> int:
        return self._agora

    def avancar(self, minutos: int) -> None:
        if minutos < 0:
            raise ValueError("o relógio não volta no tempo")
        self._agora += minutos

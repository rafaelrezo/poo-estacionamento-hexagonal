from abc import ABC, abstractmethod

from estacionamento.dominio.erros import ErroEstacionamento


class Tarifa(ABC):
    """Strategy: o serviço cobra pela permanência sem saber qual regra está em uso.
    Valores em centavos evitam erros de arredondamento com ponto flutuante."""

    @abstractmethod
    def calcular(self, minutos: int) -> int:
        """Devolve o valor em centavos para a permanência informada."""


class TarifaPorHora(Tarifa):
    """Tolerância gratuita; depois dela, cobra cada hora iniciada."""

    def __init__(self, centavos_por_hora: int, tolerancia_minutos: int):
        if centavos_por_hora <= 0 or tolerancia_minutos < 0:
            raise ErroEstacionamento("tarifa por hora com parâmetros inválidos")
        self._centavos_por_hora = centavos_por_hora
        self._tolerancia_minutos = tolerancia_minutos

    def calcular(self, minutos: int) -> int:
        if minutos < 0:
            raise ErroEstacionamento("permanência negativa")
        if minutos <= self._tolerancia_minutos:
            return 0
        horas_iniciadas = (minutos + 59) // 60
        return horas_iniciadas * self._centavos_por_hora


class TarifaFixa(Tarifa):
    """Valor único por permanência, como em dias de evento."""

    def __init__(self, centavos: int):
        if centavos <= 0:
            raise ErroEstacionamento("tarifa fixa deve ser positiva")
        self._centavos = centavos

    def calcular(self, minutos: int) -> int:
        if minutos < 0:
            raise ErroEstacionamento("permanência negativa")
        return self._centavos

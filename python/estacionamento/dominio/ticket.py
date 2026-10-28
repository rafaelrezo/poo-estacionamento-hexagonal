from typing import Optional

from estacionamento.dominio.erros import ErroEstacionamento
from estacionamento.dominio.placa import Placa
from estacionamento.dominio.tarifa import Tarifa


class Ticket:
    """Registro de uma permanência. Horários são minutos contados por um relógio
    externo; o domínio não sabe se eles vêm do sistema ou de uma simulação."""

    def __init__(self, placa: Placa, entrada: int):
        if entrada < 0:
            raise ErroEstacionamento("horário de entrada inválido")
        self._placa = placa
        self._entrada = entrada
        self._saida: Optional[int] = None
        self._valor_centavos: Optional[int] = None

    @classmethod
    def restaurar(cls, placa: Placa, entrada: int, saida: Optional[int],
                  valor_centavos: Optional[int]) -> "Ticket":
        """Reconstrói um ticket gravado; usado pelos adaptadores de persistência."""
        ticket = cls(placa, entrada)
        if (saida is None) != (valor_centavos is None):
            raise ErroEstacionamento("ticket gravado sem saída e valor coerentes")
        if saida is not None and valor_centavos is not None:
            if saida < entrada or valor_centavos < 0:
                raise ErroEstacionamento("ticket gravado com saída ou valor inválido")
            ticket._saida = saida
            ticket._valor_centavos = valor_centavos
        return ticket

    def fechar(self, saida: int, tarifa: Tarifa) -> None:
        if not self.aberto:
            raise ErroEstacionamento(f"ticket de {self._placa.texto} já foi fechado")
        if saida < self._entrada:
            raise ErroEstacionamento("horário de saída anterior à entrada")
        # Calcula antes de alterar o estado: se a tarifa falhar, o ticket continua aberto.
        valor = tarifa.calcular(saida - self._entrada)
        self._saida = saida
        self._valor_centavos = valor

    @property
    def placa(self) -> Placa:
        return self._placa

    @property
    def entrada(self) -> int:
        return self._entrada

    @property
    def aberto(self) -> bool:
        return self._saida is None

    @property
    def saida(self) -> Optional[int]:
        return self._saida

    @property
    def valor_centavos(self) -> Optional[int]:
        return self._valor_centavos

    @property
    def permanencia(self) -> Optional[int]:
        if self._saida is None:
            return None
        return self._saida - self._entrada

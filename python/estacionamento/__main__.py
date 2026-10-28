"""Ponto de montagem (composition root): o único lugar que conhece todas as
classes concretas. Trocar uma tecnologia muda esta montagem, não o núcleo.

Execute a partir da pasta python/:  python3 -m estacionamento --vagas 2
"""

import argparse
import sys

from estacionamento.adaptadores.entrada.interface_texto import InterfaceTexto
from estacionamento.adaptadores.saida.relogios import RelogioSimulado, RelogioSistema
from estacionamento.adaptadores.saida.repositorio_memoria import RepositorioMemoria
from estacionamento.adaptadores.saida.repositorio_sqlite import RepositorioSQLite
from estacionamento.aplicacao.servico import ServicoEstacionamento
from estacionamento.dominio.erros import ErroEstacionamento
from estacionamento.dominio.tarifa import TarifaFixa, TarifaPorHora


def ler_opcoes(argumentos):
    parser = argparse.ArgumentParser(prog="estacionamento")
    parser.add_argument("--vagas", type=int, default=3)
    parser.add_argument("--tarifa", choices=["hora", "fixa"], default="hora")
    parser.add_argument("--relogio", choices=["simulado", "sistema"], default="simulado")
    parser.add_argument("--banco", default="", help="arquivo SQLite; vazio usa memória")
    return parser.parse_args(argumentos)


def main(argumentos=None) -> int:
    opcoes = ler_opcoes(argumentos)

    # Estratégia de cobrança.
    if opcoes.tarifa == "fixa":
        tarifa = TarifaFixa(2000)          # R$ 20,00 por permanência
    else:
        tarifa = TarifaPorHora(800, 15)    # R$ 8,00 por hora iniciada, 15 min grátis

    # Adaptadores de saída.
    simulado = RelogioSimulado(8 * 60)     # começa às 08:00
    relogio = RelogioSistema() if opcoes.relogio == "sistema" else simulado
    repositorio = RepositorioSQLite(opcoes.banco) if opcoes.banco else RepositorioMemoria()

    try:
        # Núcleo e adaptador de entrada.
        servico = ServicoEstacionamento(opcoes.vagas, tarifa, repositorio, relogio)
        interface = InterfaceTexto(servico, simulado if opcoes.relogio == "simulado" else None)
        interface.executar(sys.stdin, sys.stdout)
        return 0
    except ErroEstacionamento as erro:
        print(f"falha: {erro}", file=sys.stderr)
        return 1
    finally:
        if isinstance(repositorio, RepositorioSQLite):
            repositorio.fechar_conexao()


if __name__ == "__main__":
    sys.exit(main())

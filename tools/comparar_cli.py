"""Executa a mesma sessão nas interfaces C++ e Python e compara com a saída esperada.
As duas implementações devem se comportar de forma idêntica.

Uso: python3 tools/comparar_cli.py --cpp build/estacionamento
"""

import argparse
import difflib
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SESSAO = RAIZ / "exemplos" / "sessao.txt"
ESPERADA = RAIZ / "exemplos" / "sessao_esperada.txt"
OPCOES = ["--vagas", "2", "--relogio", "simulado"]


def executar(comando, pasta):
    ambiente = dict(os.environ, PYTHONIOENCODING="utf-8")
    resultado = subprocess.run(comando, cwd=pasta, input=SESSAO.read_bytes(),
                               capture_output=True, env=ambiente, timeout=30, check=False)
    return resultado.returncode, resultado.stdout.decode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpp", required=True)
    args = parser.parse_args()

    esperada = ESPERADA.read_text(encoding="utf-8")
    candidatos = {
        "C++": ([str(Path(args.cpp).resolve()), *OPCOES], RAIZ),
        "Python": ([sys.executable, "-m", "estacionamento", *OPCOES], RAIZ / "python"),
    }
    falhou = False
    for nome, (comando, pasta) in candidatos.items():
        codigo, saida = executar(comando, pasta)
        if codigo == 0 and saida == esperada:
            print(f"ok: interface {nome} reproduz exemplos/sessao_esperada.txt")
            continue
        falhou = True
        print(f"FALHOU: interface {nome} (código de saída {codigo})")
        diferenca = difflib.unified_diff(esperada.splitlines(), saida.splitlines(),
                                         "esperada", nome, lineterm="")
        print("\n".join(diferenca))
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())

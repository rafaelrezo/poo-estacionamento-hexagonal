"""Verifica a regra de dependência: o núcleo (dominio e aplicacao) não depende
de adaptadores nem de tecnologias de entrada e saída.

Uso: python3 tools/verificar_arquitetura.py
"""

import ast
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Camadas de projeto que cada camada pode usar.
PERMITIDAS = {
    "dominio": {"dominio"},
    "aplicacao": {"dominio", "aplicacao"},
    "adaptadores": {"dominio", "aplicacao", "adaptadores"},
}

# Tecnologias de E/S proibidas no núcleo.
CPP_PROIBIDOS = {"iostream", "fstream", "cstdio", "chrono", "filesystem", "ctime", "thread"}
PY_PROIBIDOS = {"sqlite3", "time", "datetime", "sys", "os", "io", "argparse", "pathlib",
                "socket", "subprocess", "json"}

INCLUDE = re.compile(r'^\s*#\s*include\s*([<"])([^>"]+)[>"]')


def verificar_cpp(violacoes):
    total = 0
    for camada in PERMITIDAS:
        for arquivo in sorted((RAIZ / "cpp" / camada).rglob("*.[ch]pp")):
            total += 1
            relativo = arquivo.relative_to(RAIZ)
            for numero, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
                encontrado = INCLUDE.match(linha)
                if not encontrado:
                    continue
                delimitador, incluido = encontrado.groups()
                if delimitador == '"':
                    destino = incluido.split("/")[0]
                    if destino not in PERMITIDAS[camada]:
                        violacoes.append(f"{relativo}:{numero} inclui \"{incluido}\": "
                                         f"{camada} não pode depender de {destino}")
                elif camada != "adaptadores" and incluido in CPP_PROIBIDOS:
                    violacoes.append(f"{relativo}:{numero} inclui <{incluido}>: "
                                     f"E/S pertence a um adaptador, não a {camada}")
    return total


def modulos_importados(arvore, pacote_atual):
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for nome in no.names:
                yield no.lineno, nome.name
        elif isinstance(no, ast.ImportFrom):
            if no.level:  # import relativo: resolve a partir do pacote atual
                base = pacote_atual.split(".")[: len(pacote_atual.split(".")) - no.level + 1]
                yield no.lineno, ".".join(base + ([no.module] if no.module else []))
            else:
                yield no.lineno, no.module or ""


def verificar_python(violacoes):
    total = 0
    pacote = RAIZ / "python" / "estacionamento"
    for camada in PERMITIDAS:
        for arquivo in sorted((pacote / camada).rglob("*.py")):
            total += 1
            relativo = arquivo.relative_to(RAIZ)
            partes = arquivo.relative_to(RAIZ / "python").with_suffix("").parts
            pacote_atual = ".".join(partes[:-1])
            arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
            for numero, modulo in modulos_importados(arvore, pacote_atual):
                nomes = modulo.split(".")
                if nomes[0] == "estacionamento" and len(nomes) > 1:
                    if nomes[1] not in PERMITIDAS[camada]:
                        violacoes.append(f"{relativo}:{numero} importa {modulo}: "
                                         f"{camada} não pode depender de {nomes[1]}")
                elif camada != "adaptadores" and nomes[0] in PY_PROIBIDOS:
                    violacoes.append(f"{relativo}:{numero} importa {modulo}: "
                                     f"E/S pertence a um adaptador, não a {camada}")
    return total


def main():
    violacoes = []
    total_cpp = verificar_cpp(violacoes)
    total_py = verificar_python(violacoes)
    if violacoes:
        print("FALHOU: regra de dependência violada")
        for violacao in violacoes:
            print(f"  - {violacao}")
        print("Mova a decisão de E/S para um adaptador e ofereça ao núcleo uma porta.")
        return 1
    print(f"ok: regra de dependência respeitada ({total_cpp} arquivos C++, "
          f"{total_py} arquivos Python)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

import string

from estacionamento.dominio.erros import ErroEstacionamento

LETRAS = set(string.ascii_uppercase)
DIGITOS = set(string.digits)


def _normalizar(texto: str) -> str:
    return "".join(c.upper() if c.isascii() else c for c in texto if c != "-")


class Placa:
    """Objeto de valor: só existe se o texto respeitar o formato antigo (ABC1234)
    ou o Mercosul (ABC1D23). Hífen e letras minúsculas são normalizados."""

    def __init__(self, texto: str):
        normalizada = _normalizar(texto)
        valida = (
            len(normalizada) == 7
            and all(c in LETRAS for c in normalizada[:3])
            and normalizada[3] in DIGITOS
            and (normalizada[4] in LETRAS or normalizada[4] in DIGITOS)
            and all(c in DIGITOS for c in normalizada[5:])
        )
        if not valida:
            raise ErroEstacionamento(f"placa inválida: {texto}")
        self._texto = normalizada

    @property
    def texto(self) -> str:
        return self._texto

    def __eq__(self, outra: object) -> bool:
        return isinstance(outra, Placa) and self._texto == outra._texto

    def __hash__(self) -> int:
        return hash(self._texto)

    def __repr__(self) -> str:
        return f"Placa({self._texto!r})"

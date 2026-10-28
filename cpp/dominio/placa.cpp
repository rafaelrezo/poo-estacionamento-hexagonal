#include "dominio/placa.hpp"

#include <cctype>

#include "dominio/erros.hpp"

namespace estacionamento {

namespace {

bool letra(char c) { return c >= 'A' && c <= 'Z'; }
bool digito(char c) { return c >= '0' && c <= '9'; }

std::string normalizar(const std::string& texto) {
    std::string resultado;
    for (char c : texto) {
        if (c != '-') {
            resultado += static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
        }
    }
    return resultado;
}

}  // namespace

Placa::Placa(const std::string& texto) : texto_(normalizar(texto)) {
    const bool valida = texto_.size() == 7 && letra(texto_[0]) && letra(texto_[1]) &&
                        letra(texto_[2]) && digito(texto_[3]) &&
                        (letra(texto_[4]) || digito(texto_[4])) && digito(texto_[5]) &&
                        digito(texto_[6]);
    if (!valida) {
        throw ErroEstacionamento("placa inválida: " + texto);
    }
}

}  // namespace estacionamento

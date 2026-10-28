#pragma once

// Mini-harness de testes sem bibliotecas externas: cada verificação imprime
// "ok" ou "FALHOU" e o programa retorna 1 se alguma falhar.

#include <exception>
#include <iostream>
#include <string>

#include "dominio/erros.hpp"

namespace teste {

inline int falhas = 0;

inline void verificar(bool condicao, const std::string& descricao) {
    std::cout << (condicao ? "ok: " : "FALHOU: ") << descricao << '\n';
    if (!condicao) {
        ++falhas;
    }
}

// Executa a ação e devolve a mensagem do ErroEstacionamento, ou "" se nada foi lançado.
template <typename Acao>
std::string mensagem_de_erro(Acao acao) {
    try {
        acao();
    } catch (const estacionamento::ErroEstacionamento& erro) {
        return erro.what();
    }
    return "";
}

inline int resultado(const std::string& suite) {
    std::cout << suite << ": " << (falhas == 0 ? "todas as verificações passaram" : "há falhas")
              << "\n\n";
    return falhas == 0 ? 0 : 1;
}

}  // namespace teste

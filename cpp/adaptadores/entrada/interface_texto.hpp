#pragma once

#include <iosfwd>
#include <string>

#include "adaptadores/saida/relogios.hpp"
#include "aplicacao/servico_estacionamento.hpp"

namespace estacionamento {

// Adaptador de entrada: traduz linhas de texto em chamadas aos casos de uso e
// traduz os resultados em mensagens. Formatar dinheiro e horário é papel dele.
class InterfaceTexto {
public:
    // relogio_simulado pode ser nulo; nesse caso o comando "avancar" é recusado.
    InterfaceTexto(ServicoEstacionamento& servico, RelogioSimulado* relogio_simulado);

    void executar(std::istream& entrada, std::ostream& saida);

private:
    void tratar(const std::string& comando, const std::string& argumento, std::ostream& saida);

    ServicoEstacionamento& servico_;
    RelogioSimulado* relogio_simulado_;
};

}  // namespace estacionamento

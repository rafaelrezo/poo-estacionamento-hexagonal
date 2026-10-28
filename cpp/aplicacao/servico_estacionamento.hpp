#pragma once

#include <string>
#include <vector>

#include "aplicacao/portas.hpp"
#include "dominio/tarifa.hpp"
#include "dominio/ticket.hpp"

namespace estacionamento {

// Porta de entrada: as operações públicas deste serviço são os casos de uso.
// Ele coordena domínio e portas; não lê teclado, não escreve arquivo.
class ServicoEstacionamento {
public:
    ServicoEstacionamento(int capacidade, const Tarifa& tarifa,
                          RepositorioTickets& repositorio, const Relogio& relogio);

    Ticket registrar_entrada(const std::string& placa);
    Ticket registrar_saida(const std::string& placa);
    int vagas_livres() const;
    int capacidade() const { return capacidade_; }
    std::vector<Ticket> historico() const;

private:
    int capacidade_;
    const Tarifa& tarifa_;
    RepositorioTickets& repositorio_;
    const Relogio& relogio_;
};

}  // namespace estacionamento

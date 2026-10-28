#include "dominio/ticket.hpp"

#include <utility>

#include "dominio/erros.hpp"

namespace estacionamento {

Ticket::Ticket(Placa placa, int entrada) : placa_(std::move(placa)), entrada_(entrada) {
    if (entrada < 0) {
        throw ErroEstacionamento("horário de entrada inválido");
    }
}

Ticket Ticket::restaurar(Placa placa, int entrada, std::optional<int> saida,
                         std::optional<int> valor_centavos) {
    Ticket ticket(std::move(placa), entrada);
    if (saida.has_value() != valor_centavos.has_value()) {
        throw ErroEstacionamento("ticket gravado sem saída e valor coerentes");
    }
    if (saida.has_value()) {
        if (*saida < entrada || *valor_centavos < 0) {
            throw ErroEstacionamento("ticket gravado com saída ou valor inválido");
        }
        ticket.saida_ = saida;
        ticket.valor_centavos_ = valor_centavos;
    }
    return ticket;
}

void Ticket::fechar(int saida, const Tarifa& tarifa) {
    if (!aberto()) {
        throw ErroEstacionamento("ticket de " + placa_.texto() + " já foi fechado");
    }
    if (saida < entrada_) {
        throw ErroEstacionamento("horário de saída anterior à entrada");
    }
    // Calcula antes de alterar o estado: se a tarifa falhar, o ticket continua aberto.
    const int valor = tarifa.calcular(saida - entrada_);
    saida_ = saida;
    valor_centavos_ = valor;
}

std::optional<int> Ticket::permanencia() const {
    if (!saida_.has_value()) {
        return std::nullopt;
    }
    return *saida_ - entrada_;
}

}  // namespace estacionamento

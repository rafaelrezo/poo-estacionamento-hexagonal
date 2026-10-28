#include "adaptadores/saida/repositorio_memoria.hpp"

#include <algorithm>

namespace estacionamento {

void RepositorioMemoria::salvar(const Ticket& ticket) {
    for (Ticket& existente : tickets_) {
        if (existente.aberto() && existente.placa() == ticket.placa()) {
            existente = ticket;
            return;
        }
    }
    tickets_.push_back(ticket);
}

std::optional<Ticket> RepositorioMemoria::buscar_aberto(const Placa& placa) const {
    for (const Ticket& ticket : tickets_) {
        if (ticket.aberto() && ticket.placa() == placa) {
            return ticket;
        }
    }
    return std::nullopt;
}

int RepositorioMemoria::contar_abertos() const {
    return static_cast<int>(std::count_if(tickets_.begin(), tickets_.end(),
                                          [](const Ticket& t) { return t.aberto(); }));
}

std::vector<Ticket> RepositorioMemoria::listar() const { return tickets_; }

}  // namespace estacionamento

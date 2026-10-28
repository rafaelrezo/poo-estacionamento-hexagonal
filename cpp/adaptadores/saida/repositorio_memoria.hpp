#pragma once

#include <vector>

#include "aplicacao/portas.hpp"

namespace estacionamento {

// Adaptador mais simples da porta: útil em testes e demonstrações.
class RepositorioMemoria : public RepositorioTickets {
public:
    void salvar(const Ticket& ticket) override;
    std::optional<Ticket> buscar_aberto(const Placa& placa) const override;
    int contar_abertos() const override;
    std::vector<Ticket> listar() const override;

private:
    std::vector<Ticket> tickets_;
};

}  // namespace estacionamento

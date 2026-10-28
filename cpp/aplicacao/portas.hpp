#pragma once

#include <optional>
#include <vector>

#include "dominio/placa.hpp"
#include "dominio/ticket.hpp"

namespace estacionamento {

// Portas de saída: o que o núcleo precisa do mundo externo, descrito nos termos
// do próprio núcleo. Quem implementa são os adaptadores; quem escolhe é o main.

class RepositorioTickets {
public:
    virtual ~RepositorioTickets() = default;

    // Substitui o ticket aberto da mesma placa ou, se não houver, acrescenta.
    virtual void salvar(const Ticket& ticket) = 0;
    virtual std::optional<Ticket> buscar_aberto(const Placa& placa) const = 0;
    virtual int contar_abertos() const = 0;
    virtual std::vector<Ticket> listar() const = 0;
};

class Relogio {
public:
    virtual ~Relogio() = default;
    virtual int agora_em_minutos() const = 0;
};

}  // namespace estacionamento

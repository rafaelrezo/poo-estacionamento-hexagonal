#pragma once

#include <optional>

#include "dominio/placa.hpp"
#include "dominio/tarifa.hpp"

namespace estacionamento {

// Registro de uma permanência. Horários são minutos contados por um relógio
// externo; o domínio não sabe se eles vêm do sistema ou de uma simulação.
class Ticket {
public:
    Ticket(Placa placa, int entrada);

    // Reconstrói um ticket gravado; usado pelos adaptadores de persistência.
    static Ticket restaurar(Placa placa, int entrada, std::optional<int> saida,
                            std::optional<int> valor_centavos);

    void fechar(int saida, const Tarifa& tarifa);

    const Placa& placa() const { return placa_; }
    int entrada() const { return entrada_; }
    bool aberto() const { return !saida_.has_value(); }
    std::optional<int> saida() const { return saida_; }
    std::optional<int> valor_centavos() const { return valor_centavos_; }
    std::optional<int> permanencia() const;

private:
    Placa placa_;
    int entrada_;
    std::optional<int> saida_;
    std::optional<int> valor_centavos_;
};

}  // namespace estacionamento

#pragma once

#include "aplicacao/portas.hpp"

namespace estacionamento {

// Minutos desde 1970-01-01 em UTC, lidos do relógio do computador.
class RelogioSistema : public Relogio {
public:
    int agora_em_minutos() const override;
};

// Relógio controlado: torna demonstrações e testes reproduzíveis.
class RelogioSimulado : public Relogio {
public:
    explicit RelogioSimulado(int inicio);
    int agora_em_minutos() const override { return agora_; }
    void avancar(int minutos);

private:
    int agora_;
};

}  // namespace estacionamento

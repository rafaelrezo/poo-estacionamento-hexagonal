#pragma once

namespace estacionamento {

// Strategy: o serviço cobra pela permanência sem saber qual regra está em uso.
// Valores em centavos evitam erros de arredondamento com ponto flutuante.
class Tarifa {
public:
    virtual ~Tarifa() = default;
    virtual int calcular(int minutos) const = 0;
};

// Tolerância gratuita; depois dela, cobra cada hora iniciada.
class TarifaPorHora : public Tarifa {
public:
    TarifaPorHora(int centavos_por_hora, int tolerancia_minutos);
    int calcular(int minutos) const override;

private:
    int centavos_por_hora_;
    int tolerancia_minutos_;
};

// Valor único por permanência, como em dias de evento.
class TarifaFixa : public Tarifa {
public:
    explicit TarifaFixa(int centavos);
    int calcular(int minutos) const override;

private:
    int centavos_;
};

}  // namespace estacionamento

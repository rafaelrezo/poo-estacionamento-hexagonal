#include "dominio/tarifa.hpp"

#include "dominio/erros.hpp"

namespace estacionamento {

TarifaPorHora::TarifaPorHora(int centavos_por_hora, int tolerancia_minutos)
    : centavos_por_hora_(centavos_por_hora), tolerancia_minutos_(tolerancia_minutos) {
    if (centavos_por_hora <= 0 || tolerancia_minutos < 0) {
        throw ErroEstacionamento("tarifa por hora com parâmetros inválidos");
    }
}

int TarifaPorHora::calcular(int minutos) const {
    if (minutos < 0) {
        throw ErroEstacionamento("permanência negativa");
    }
    if (minutos <= tolerancia_minutos_) {
        return 0;
    }
    const int horas_iniciadas = (minutos + 59) / 60;
    return horas_iniciadas * centavos_por_hora_;
}

TarifaFixa::TarifaFixa(int centavos) : centavos_(centavos) {
    if (centavos <= 0) {
        throw ErroEstacionamento("tarifa fixa deve ser positiva");
    }
}

int TarifaFixa::calcular(int minutos) const {
    if (minutos < 0) {
        throw ErroEstacionamento("permanência negativa");
    }
    return centavos_;
}

}  // namespace estacionamento

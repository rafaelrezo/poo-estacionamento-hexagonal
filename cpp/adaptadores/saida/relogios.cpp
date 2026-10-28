#include "adaptadores/saida/relogios.hpp"

#include <chrono>
#include <stdexcept>

namespace estacionamento {

int RelogioSistema::agora_em_minutos() const {
    using namespace std::chrono;
    return static_cast<int>(duration_cast<minutes>(system_clock::now().time_since_epoch()).count());
}

RelogioSimulado::RelogioSimulado(int inicio) : agora_(inicio) {
    if (inicio < 0) {
        throw std::invalid_argument("relógio simulado não pode começar antes de zero");
    }
}

void RelogioSimulado::avancar(int minutos) {
    if (minutos < 0) {
        throw std::invalid_argument("o relógio não volta no tempo");
    }
    agora_ += minutos;
}

}  // namespace estacionamento

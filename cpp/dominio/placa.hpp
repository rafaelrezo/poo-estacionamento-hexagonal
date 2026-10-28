#pragma once

#include <string>

namespace estacionamento {

// Objeto de valor: só existe se o texto respeitar o formato antigo (ABC1234)
// ou o Mercosul (ABC1D23). Hífen e letras minúsculas são normalizados.
class Placa {
public:
    explicit Placa(const std::string& texto);

    const std::string& texto() const { return texto_; }
    bool operator==(const Placa& outra) const { return texto_ == outra.texto_; }

private:
    std::string texto_;
};

}  // namespace estacionamento

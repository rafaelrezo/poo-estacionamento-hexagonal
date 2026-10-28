#pragma once

#include <stdexcept>

namespace estacionamento {

// Violação de uma regra do negócio. Os adaptadores decidem como mostrá-la.
class ErroEstacionamento : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

}  // namespace estacionamento

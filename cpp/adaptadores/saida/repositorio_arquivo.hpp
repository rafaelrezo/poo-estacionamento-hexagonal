#pragma once

#include <string>
#include <vector>

#include "adaptadores/saida/repositorio_memoria.hpp"
#include "aplicacao/portas.hpp"

namespace estacionamento {

// Mesma porta, outra tecnologia: um arquivo texto com uma linha por ticket,
// no formato placa;entrada;saida;valor ("-" indica campo vazio).
// Reaproveita o repositório em memória por composição e regrava o arquivo a cada
// alteração. É simples de ler, mas não protege contra dois processos simultâneos.
class RepositorioArquivo : public RepositorioTickets {
public:
    explicit RepositorioArquivo(std::string caminho);

    void salvar(const Ticket& ticket) override;
    std::optional<Ticket> buscar_aberto(const Placa& placa) const override;
    int contar_abertos() const override;
    std::vector<Ticket> listar() const override;

private:
    void carregar();
    void gravar() const;

    std::string caminho_;
    RepositorioMemoria memoria_;
};

}  // namespace estacionamento

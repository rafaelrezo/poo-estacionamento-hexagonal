#include "aplicacao/servico_estacionamento.hpp"

#include "dominio/erros.hpp"

namespace estacionamento {

ServicoEstacionamento::ServicoEstacionamento(int capacidade, const Tarifa& tarifa,
                                             RepositorioTickets& repositorio,
                                             const Relogio& relogio)
    : capacidade_(capacidade), tarifa_(tarifa), repositorio_(repositorio), relogio_(relogio) {
    if (capacidade <= 0) {
        throw ErroEstacionamento("capacidade deve ser positiva");
    }
}

Ticket ServicoEstacionamento::registrar_entrada(const std::string& texto) {
    const Placa placa(texto);
    if (repositorio_.buscar_aberto(placa).has_value()) {
        throw ErroEstacionamento(placa.texto() + " já está no pátio");
    }
    if (vagas_livres() == 0) {
        throw ErroEstacionamento("pátio lotado");
    }
    const Ticket ticket(placa, relogio_.agora_em_minutos());
    repositorio_.salvar(ticket);
    return ticket;
}

Ticket ServicoEstacionamento::registrar_saida(const std::string& texto) {
    const Placa placa(texto);
    std::optional<Ticket> aberto = repositorio_.buscar_aberto(placa);
    if (!aberto.has_value()) {
        throw ErroEstacionamento("não há entrada aberta para " + placa.texto());
    }
    aberto->fechar(relogio_.agora_em_minutos(), tarifa_);
    repositorio_.salvar(*aberto);
    return *aberto;
}

int ServicoEstacionamento::vagas_livres() const {
    return capacidade_ - repositorio_.contar_abertos();
}

std::vector<Ticket> ServicoEstacionamento::historico() const {
    return repositorio_.listar();
}

}  // namespace estacionamento

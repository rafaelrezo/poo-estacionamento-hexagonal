#include "adaptadores/entrada/interface_texto.hpp"

#include <iostream>
#include <sstream>
#include <stdexcept>

#include "dominio/erros.hpp"

namespace estacionamento {

namespace {

// Erro de uso do comando: pertence a este adaptador, não ao domínio.
class ErroComando : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

std::string dois_digitos(int valor) {
    return (valor < 10 ? "0" : "") + std::to_string(valor);
}

std::string formatar_horario(int minutos) {
    const int do_dia = minutos % (24 * 60);
    return dois_digitos(do_dia / 60) + ":" + dois_digitos(do_dia % 60);
}

std::string formatar_reais(int centavos) {
    return "R$ " + std::to_string(centavos / 100) + "," + dois_digitos(centavos % 100);
}

int ler_minutos(const std::string& texto) {
    if (texto.empty() || texto.find_first_not_of("0123456789") != std::string::npos ||
        texto.size() > 6) {
        throw ErroComando("avancar exige minutos inteiros não negativos");
    }
    return std::stoi(texto);
}

void exigir(const std::string& argumento, const std::string& uso) {
    if (argumento.empty()) {
        throw ErroComando("uso: " + uso);
    }
}

}  // namespace

InterfaceTexto::InterfaceTexto(ServicoEstacionamento& servico, RelogioSimulado* relogio_simulado)
    : servico_(servico), relogio_simulado_(relogio_simulado) {}

void InterfaceTexto::executar(std::istream& entrada, std::ostream& saida) {
    std::string linha;
    while (std::getline(entrada, linha)) {
        std::istringstream partes(linha);
        std::string comando, argumento;
        partes >> comando >> argumento;
        if (comando.empty() || comando[0] == '#') {
            continue;
        }
        if (comando == "sair") {
            break;
        }
        try {
            tratar(comando, argumento, saida);
        } catch (const ErroEstacionamento& erro) {
            saida << "erro: " << erro.what() << '\n';
        } catch (const ErroComando& erro) {
            saida << "erro: " << erro.what() << '\n';
        }
    }
}

void InterfaceTexto::tratar(const std::string& comando, const std::string& argumento,
                            std::ostream& saida) {
    if (comando == "entrada") {
        exigir(argumento, "entrada PLACA");
        const Ticket ticket = servico_.registrar_entrada(argumento);
        saida << "entrada registrada: " << ticket.placa().texto() << " às "
              << formatar_horario(ticket.entrada())
              << " (vagas livres: " << servico_.vagas_livres() << ")\n";
    } else if (comando == "saida") {
        exigir(argumento, "saida PLACA");
        const Ticket ticket = servico_.registrar_saida(argumento);
        saida << "saída registrada: " << ticket.placa().texto() << " | "
              << *ticket.permanencia() << " min | " << formatar_reais(*ticket.valor_centavos())
              << '\n';
    } else if (comando == "avancar") {
        if (relogio_simulado_ == nullptr) {
            throw ErroComando("o relógio do sistema não pode ser avançado");
        }
        relogio_simulado_->avancar(ler_minutos(argumento));
        saida << "relógio: " << formatar_horario(relogio_simulado_->agora_em_minutos()) << '\n';
    } else if (comando == "vagas") {
        saida << "vagas livres: " << servico_.vagas_livres() << " de " << servico_.capacidade()
              << '\n';
    } else if (comando == "historico") {
        const auto tickets = servico_.historico();
        if (tickets.empty()) {
            saida << "histórico vazio\n";
        }
        for (const Ticket& ticket : tickets) {
            saida << ticket.placa().texto() << " | " << formatar_horario(ticket.entrada()) << " -> ";
            if (ticket.aberto()) {
                saida << "no pátio\n";
            } else {
                saida << formatar_horario(*ticket.saida()) << " | " << *ticket.permanencia()
                      << " min | " << formatar_reais(*ticket.valor_centavos()) << '\n';
            }
        }
    } else if (comando == "ajuda") {
        saida << "comandos: entrada PLACA, saida PLACA, avancar MINUTOS, vagas, historico, "
                 "ajuda, sair\n";
    } else {
        throw ErroComando("comando desconhecido: " + comando + " (digite ajuda)");
    }
}

}  // namespace estacionamento

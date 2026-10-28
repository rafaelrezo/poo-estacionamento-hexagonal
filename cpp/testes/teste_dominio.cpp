// O domínio é testado sem portas nem adaptadores: só objetos e valores.

#include "dominio/placa.hpp"
#include "dominio/tarifa.hpp"
#include "dominio/ticket.hpp"
#include "testes/verificacao.hpp"

using namespace estacionamento;
using teste::mensagem_de_erro;
using teste::verificar;

int main() {
    verificar(Placa("abc-1d23").texto() == "ABC1D23", "placa Mercosul é normalizada");
    verificar(Placa("ABC1234").texto() == "ABC1234", "placa no formato antigo é aceita");
    verificar(mensagem_de_erro([] { Placa("AB12345"); }) == "placa inválida: AB12345",
              "placa com duas letras é recusada");
    verificar(mensagem_de_erro([] { Placa("ABCD123"); }) == "placa inválida: ABCD123",
              "placa com quatro letras é recusada");

    const TarifaPorHora por_hora(800, 15);
    verificar(por_hora.calcular(15) == 0, "15 min ainda estão na tolerância");
    verificar(por_hora.calcular(16) == 800, "16 min cobram a primeira hora");
    verificar(por_hora.calcular(60) == 800, "60 min cobram uma hora");
    verificar(por_hora.calcular(61) == 1600, "61 min cobram duas horas iniciadas");
    verificar(mensagem_de_erro([&] { por_hora.calcular(-1); }) == "permanência negativa",
              "permanência negativa é recusada");
    verificar(TarifaFixa(2000).calcular(300) == 2000, "tarifa fixa não depende do tempo");

    Ticket ticket(Placa("ABC1D23"), 480);
    verificar(ticket.aberto() && !ticket.permanencia().has_value(), "ticket novo está aberto");
    verificar(mensagem_de_erro([&] { ticket.fechar(479, por_hora); }) ==
                  "horário de saída anterior à entrada",
              "saída antes da entrada é recusada");
    verificar(ticket.aberto(), "ticket continua aberto após saída recusada");
    ticket.fechar(575, por_hora);
    verificar(!ticket.aberto() && *ticket.permanencia() == 95 && *ticket.valor_centavos() == 1600,
              "ticket fechado guarda 95 min e R$ 16,00");
    verificar(mensagem_de_erro([&] { ticket.fechar(600, por_hora); }) ==
                  "ticket de ABC1D23 já foi fechado",
              "ticket não é fechado duas vezes");
    verificar(mensagem_de_erro([] { Ticket::restaurar(Placa("ABC1D23"), 480, 500, std::nullopt); }) ==
                  "ticket gravado sem saída e valor coerentes",
              "restauração incoerente é recusada");

    return teste::resultado("domínio");
}

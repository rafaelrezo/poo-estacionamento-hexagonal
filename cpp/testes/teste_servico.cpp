// Os casos de uso são testados com adaptadores leves: repositório em memória e
// relógio simulado. Nenhum arquivo, terminal ou banco é necessário.

#include "adaptadores/saida/relogios.hpp"
#include "adaptadores/saida/repositorio_memoria.hpp"
#include "aplicacao/servico_estacionamento.hpp"
#include "testes/verificacao.hpp"

using namespace estacionamento;
using teste::mensagem_de_erro;
using teste::verificar;

int main() {
    const TarifaPorHora tarifa(800, 15);
    RepositorioMemoria repositorio;
    RelogioSimulado relogio(480);
    ServicoEstacionamento servico(2, tarifa, repositorio, relogio);

    servico.registrar_entrada("ABC1D23");
    verificar(servico.vagas_livres() == 1, "entrada ocupa uma vaga");
    verificar(mensagem_de_erro([&] { servico.registrar_entrada("abc-1d23"); }) ==
                  "ABC1D23 já está no pátio",
              "mesma placa não entra duas vezes");

    servico.registrar_entrada("XYZ9876");
    verificar(mensagem_de_erro([&] { servico.registrar_entrada("QWE1R23"); }) == "pátio lotado",
              "entrada é recusada com o pátio lotado");
    verificar(mensagem_de_erro([&] { servico.registrar_saida("QWE1R23"); }) ==
                  "não há entrada aberta para QWE1R23",
              "saída sem entrada é recusada");

    relogio.avancar(95);
    const Ticket recibo = servico.registrar_saida("ABC1D23");
    verificar(*recibo.permanencia() == 95 && *recibo.valor_centavos() == 1600,
              "saída após 95 min cobra R$ 16,00");
    verificar(servico.vagas_livres() == 1, "saída libera a vaga");

    servico.registrar_entrada("ABC1D23");
    verificar(servico.historico().size() == 3, "reentrada cria um novo ticket no histórico");

    verificar(mensagem_de_erro([&] { ServicoEstacionamento(0, tarifa, repositorio, relogio); }) ==
                  "capacidade deve ser positiva",
              "capacidade zero é recusada");

    // Trocar a estratégia não exige mudar o serviço.
    const TarifaFixa fixa(2000);
    RepositorioMemoria outro_repositorio;
    ServicoEstacionamento evento(10, fixa, outro_repositorio, relogio);
    evento.registrar_entrada("ABC1234");
    relogio.avancar(5);
    verificar(*evento.registrar_saida("ABC1234").valor_centavos() == 2000,
              "mesmo serviço cobra pela tarifa fixa");

    return teste::resultado("serviço");
}

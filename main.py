# Importa as funções refatoradas dos módulos
from src.compliance_chatbot import criar_chatbot_compliance, perguntar_ao_chatbot
from src.conspiracy_detector import verificar_conspiracao
from src.fraud_detector_simple import analisar_transacoes_simples
from src.fraud_detector_complex import analisar_transacoes_complexas
import os

def exibir_menu():
    """Exibe o menu principal para o usuário."""
    print("\n--- Auditoria do Toby: Painel de Controle (Google AI SDK) ---")
    print("1. Chatbot de Consulta de Compliance")
    print("2. Verificação de Conspiração contra Toby")
    print("3. Detecção de Fraudes Simples (Violações Diretas)")
    print("4. Detecção de Fraudes Complexas (Análise Contextual)")
    print("5. Sair")
    return input("Escolha uma opção (1-5): ")

def main():
    """Função principal que gerencia a interação com o usuário."""
    if not os.getenv("GEMINI_API_KEY"):
        print("\n[ERRO] A variável de ambiente GEMINI_API_KEY não foi definida.")
        print("Por favor, crie um arquivo .env e adicione sua chave: GEMINI_API_KEY='SUA_CHAVE_AQUI'")
        return

    chatbot_inicializado = False
    
    # Define os caminhos para os arquivos de dados
    caminho_emails = "emails_internos.txt"
    caminho_politica = "politica_compliance.txt"
    caminho_transacoes = "transacoes_bancarias.csv"

    while True:
        escolha = exibir_menu()

        if escolha == '1':
            print("\n--- Módulo: Chatbot de Compliance (Google AI SDK) ---")
            if not chatbot_inicializado:
                print("Inicializando o chatbot e criando o Vector Store...")
                criar_chatbot_compliance(caminho_politica)
                chatbot_inicializado = True
                print("Chatbot pronto!")
            
            while True:
                pergunta = input("\nFaça sua pergunta sobre a política (ou digite 'voltar'): ")
                if pergunta.lower() == 'voltar':
                    break
                resposta = perguntar_ao_chatbot(pergunta)
                print("\nResposta do Chatbot:", resposta)

        elif escolha == '2':
            print("\n--- Módulo: Verificação de Conspiração (Google AI SDK) ---")
            print("Analisando e-mails em busca de conspirações contra Toby...")
            resultado = verificar_conspiracao(caminho_emails)
            print("\n--- Relatório de Análise ---")
            print(resultado)
            print("----------------------------")
            input("\nPressione Enter para continuar...")

        elif escolha == '3':
            print("\n--- Módulo: Detecção de Fraudes Simples (Google AI SDK) ---")
            violacoes = analisar_transacoes_simples(caminho_transacoes, caminho_politica)
            print("\n--- Relatório de Violações Diretas ---")
            if not violacoes:
                print("Nenhuma violação de compliance foi detectada.")
            else:
                print(f"Total de violações detectadas: {len(violacoes)}\n")
                for violacao in violacoes:
                    transacao = violacao['transacao']
                    print(f"ID: {transacao['ID']} | Funcionário: {transacao['Funcionario']} | Valor: ${transacao['Valor']}")
                    print(f"Descrição: {transacao['Descricao']}")
                    print(f"Análise da IA: {violacao['justificativa_ia']}")
                    print("-" * 30)
            input("\nPressione Enter para continuar...")
        
        elif escolha == '4':
            print("\n--- Módulo: Detecção de Fraudes Complexas (Google AI SDK) ---")
            suspeitas = analisar_transacoes_complexas(caminho_transacoes, caminho_politica, caminho_emails)
            print("\n--- Relatório de Suspeitas Contextuais ---")
            if not suspeitas:
                print("Nenhuma suspeita de fraude contextual foi encontrada.")
            else:
                print(f"Total de suspeitas encontradas: {len(suspeitas)}\n")
                for suspeita in suspeitas:
                    transacao = suspeita['transacao']
                    print(f"ID da Transação Suspeita: {transacao['ID']} ({transacao['Funcionario']}, ${transacao['Valor']})")
                    print(f"Análise Forense da IA: {suspeita['justificativa_ia']}")
                    print("-" * 40)
            input("\nPressione Enter para continuar...")

        elif escolha == '5':
            print("Saindo do sistema de auditoria. Até mais!")
            break
        
        else:
            print("Opção inválida. Por favor, escolha um número de 1 a 5.")

if __name__ == '__main__':
    main()
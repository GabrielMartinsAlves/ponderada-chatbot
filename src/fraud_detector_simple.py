import os
import csv
import dotenv
import google.generativeai as genai

# Carrega as variáveis de ambiente e configura a API
dotenv.load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A chave de API do Gemini não foi encontrada. Defina a variável de ambiente GEMINI_API_KEY.")
genai.configure(api_key=api_key)

def ler_transacoes(caminho_arquivo):
    """Lê o arquivo CSV de transações e retorna uma lista de dicionários."""
    transacoes = []
    with open(caminho_arquivo, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            transacoes.append(row)
    return transacoes

def ler_politica(caminho_arquivo):
    """Lê o arquivo de texto da política de compliance e retorna seu conteúdo."""
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        return f.read()

def analisar_transacoes_simples(caminho_transacoes, caminho_politica):
    """
    Analisa transações bancárias em busca de violações diretas da política de compliance.
    """
    transacoes = ler_transacoes(caminho_transacoes)
    politica = ler_politica(caminho_politica)
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    violacoes_encontradas = []

    print("Iniciando análise de transações simples com o Google AI SDK...")
    
    for i, transacao in enumerate(transacoes):
        print(f"Analisando transação {i+1}/{len(transacoes)}...")
        
        detalhes_transacao = (
            f"ID: {transacao['id_transacao']}, "
            f"Data: {transacao['data']}, "
            f"Funcionário: {transacao['funcionario']}, "
            f"Valor: ${transacao['valor']}, "
            f"Descrição: {transacao['descricao']}"
        )

        prompt = f"""
        Você é um auditor de compliance da Dunder Mifflin. Sua tarefa é analisar uma transação e verificar se ela viola alguma regra da política de compliance da empresa.

        **Política de Compliance:**
        {politica}

        **Transação para Análise:**
        {detalhes_transacao}

        **Instruções:**
        1. Compare a transação com cada regra da política.
        2. Se a transação violar claramente uma ou mais regras, descreva a violação, qual regra foi quebrada e por quê.
        3. Se não houver violação, responda **exclusivamente** com a frase "Nenhuma violação detectada.".

        **Relatório de Auditoria:**
        """

        try:
            response = model.generate_content(prompt)
            resultado = response.text.strip()
            
            if "Nenhuma violação detectada." not in resultado:
                violacao = {
                    "transacao": transacao,
                    "justificativa_ia": resultado
                }
                violacoes_encontradas.append(violacao)
        except Exception as e:
            print(f"Erro ao analisar a transação {transacao['id_transacao']}: {e}")

    return violacoes_encontradas

# Exemplo de uso
if __name__ == '__main__':
    violacoes = analisar_transacoes_simples()
    
    print("\n\n--- Relatório de Detecção de Fraudes Simples ---")
    if not violacoes:
        print("Nenhuma violação de compliance foi detectada nas transações.")
    else:
        print(f"Total de violações detectadas: {len(violacoes)}\n")
        for violacao in violacoes:
            transacao = violacao['transacao']
            print(f"ID da Transação: {transacao['id_transacao']}")
            print(f"Funcionário: {transacao['funcionario']}")
            print(f"Valor: ${transacao['valor']}")
            print(f"Descrição: {transacao['descricao']}")
            print(f"Análise da IA: {violacao['justificativa_ia']}")
            print("-" * 30)
    print("-------------------------------------------------")
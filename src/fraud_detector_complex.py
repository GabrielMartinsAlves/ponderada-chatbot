import os
import csv
import re
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

def parse_emails(file_path):
    """Analisa o arquivo de texto de e-mails e o divide em uma lista de dicionários."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    email_blocks = content.strip().split('---')
    parsed_emails = []
    for block in email_blocks:
        if not block.strip():
            continue
        email_data = {}
        lines = block.strip().split('\n')
        for line in lines:
            if line.startswith('De:'):
                email_data['de'] = line.split(':', 1)[1].strip()
            elif line.startswith('Para:'):
                email_data['para'] = line.split(':', 1)[1].strip()
            elif line.startswith('Assunto:'):
                email_data['assunto'] = line.split(':', 1)[1].strip()
            elif 'corpo' not in email_data:
                email_data['corpo'] = line
            else:
                email_data['corpo'] += '\n' + line
        parsed_emails.append(email_data)
    return parsed_emails
    
def encontrar_emails_relevantes(transacao, todos_emails):
    """Encontra e-mails que podem estar relacionados a uma transação."""
    emails_relevantes = []
    funcionario = transacao['funcionario'].lower()
    palavras_chave_desc = set(re.findall(r'\b\w{4,}\b', transacao['descricao'].lower()))

    for email in todos_emails:
        de = email.get('de', '').lower()
        para = email.get('para', '').lower()
        corpo = email.get('corpo', '').lower()
        assunto = email.get('assunto', '').lower()

        if funcionario in de or funcionario in para:
            if any(palavra in corpo or palavra in assunto for palavra in palavras_chave_desc):
                emails_relevantes.append(email)
                continue
            if "despesa" in corpo or "relatório" in corpo or "reembolso" in corpo or "regra" in corpo:
                 emails_relevantes.append(email)
    return emails_relevantes

def analisar_transacoes_complexas(caminho_transacoes, caminho_politica, caminho_emails):
    """
    Analisa transações buscando fraudes que exigem o contexto de e-mails.
    """
    transacoes = ler_transacoes(caminho_transacoes)
    politica = ler_politica(caminho_politica)
    todos_emails = parse_emails(caminho_emails)
    
    # Configurações do modelo
    generation_config = {
        "temperature": 0.1,
    }
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)
    
    suspeitas_encontradas = []

    print("Iniciando análise de fraudes contextuais com o Google AI SDK...")

    for i, transacao in enumerate(transacoes):
        print(f"Analisando transação {i+1}/{len(transacoes)} para contexto...")
        
        emails_relevantes = encontrar_emails_relevantes(transacao, todos_emails)
        
        if not emails_relevantes:
            continue

        detalhes_transacao = f"ID: {transacao['id_transacao']}, Data: {transacao['data']}, Funcionário: {transacao['funcionario']}, Valor: ${transacao['valor']}, Descrição: {transacao['descricao']}"
        
        contexto_emails = ""
        for email in emails_relevantes:
            contexto_emails += f"De: {email.get('de', 'N/A')}\nPara: {email.get('para', 'N/A')}\nAssunto: {email.get('assunto', 'N/A')}\n\n{email.get('corpo', '')}\n---\n"

        prompt = f"""
        Você é um auditor forense experiente da Dunder Mifflin. Sua missão é identificar fraudes ou violações de compliance que só podem ser descobertas ao cruzar informações de transações financeiras com comunicações por e-mail.

        **Política de Compliance (resumo):**
        {politica}

        **Transação Sob Investigação:**
        {detalhes_transacao}

        **E-mails Relacionados Encontrados:**
        {contexto_emails}

        **Instruções para Análise Forense:**
        1. Analise a transação em conjunto com os e-mails.
        2. Procure por qualquer indicação de má conduta.
        3. Se você identificar uma forte suspeita de fraude ou violação contextual, descreva claramente sua análise e o porquê da suspeita, citando os e-mails e a transação.
        4. Se não houver evidência nos e-mails que levante suspeitas, responda **exclusivamente** com a frase "Nenhuma suspeita de fraude contextual.".

        **Relatório de Análise Forense:**
        """

        try:
            response = model.generate_content(prompt)
            resultado = response.text.strip()

            if "Nenhuma suspeita de fraude contextual." not in resultado:
                suspeita = {
                    "transacao": transacao,
                    "emails_relacionados": emails_relevantes,
                    "justificativa_ia": resultado
                }
                suspeitas_encontradas.append(suspeita)
        except Exception as e:
            print(f"Erro ao analisar a transação contextual {transacao['id_transacao']}: {e}")

    return suspeitas_encontradas

# Exemplo de uso
if __name__ == '__main__':
    suspeitas = analisar_transacoes_complexas()
    
    print("\n\n--- Relatório de Detecção de Fraudes Contextuais (Complexas) ---")
    if not suspeitas:
        print("Nenhuma suspeita de fraude contextual foi encontrada.")
    else:
        print(f"Total de suspeitas encontradas: {len(suspeitas)}\n")
        for suspeita in suspeitas:
            transacao = suspeita['transacao']
            print(f"ID da Transação Suspeita: {transacao['id_transacao']} ({transacao['funcionario']}, ${transacao['valor']})")
            print(f"Descrição: {transacao['descricao']}")
            print("\nAnálise Forense da IA:")
            print(suspeita['justificativa_ia'])
            print("\nE-mails Relacionados:")
            for email in suspeita['emails_relacionados']:
                print(f"  - De: {email.get('de')}, Assunto: {email.get('assunto')}")
            print("-" * 40)
    print("-----------------------------------------------------------------")
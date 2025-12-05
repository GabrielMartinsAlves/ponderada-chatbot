import os
import re
import dotenv
import google.generativeai as genai

# Carrega as variáveis de ambiente e configura a API
dotenv.load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A chave de API do Gemini não foi encontrada. Defina a variável de ambiente GEMINI_API_KEY.")
genai.configure(api_key=api_key)

def parse_emails(file_path):
    """
    Analisa o arquivo de texto de e-mails e o divide em uma lista de dicionários.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    email_blocks = content.strip().split('---')
    
    parsed_emails = []
    for block in email_blocks:
        if not block.strip():
            continue
        
        email_data = {}
        lines = block.strip().split('\n')
        
        de_match = re.search(r'^De:\s*(.*)', lines[0]) if len(lines) > 0 else None
        para_match = re.search(r'^Para:\s*(.*)', lines[1]) if len(lines) > 1 else None
        assunto_match = re.search(r'^Assunto:\s*(.*)', lines[2]) if len(lines) > 2 else None

        if de_match:
            email_data['de'] = de_match.group(1).strip()
        if para_match:
            email_data['para'] = para_match.group(1).strip()
        if assunto_match:
            email_data['assunto'] = assunto_match.group(1).strip()
            
        body_start_index = 3 if assunto_match else 2 if para_match else 1 if de_match else 0
        email_data['corpo'] = '\n'.join(lines[body_start_index:]).strip()
        
        parsed_emails.append(email_data)
        
    return parsed_emails

def verificar_conspiracao(caminho_arquivo_emails):
    """
    Verifica se há emails de Michael Scott que indicam uma conspiração contra Toby.
    """
    todos_emails = parse_emails(caminho_arquivo_emails)
    
    emails_relevantes = []
    for email in todos_emails:
        is_from_michael = email.get('de', '').lower() == 'michael scott'
        mentions_toby = 'toby' in email.get('corpo', '').lower() or 'toby' in email.get('assunto', '').lower()
        
        if is_from_michael and mentions_toby:
            emails_relevantes.append(email)
            
    if not emails_relevantes:
        return "Nenhuma evidência de conspiração encontrada nos e-mails de Michael Scott contra Toby."

    contexto = ""
    for i, email in enumerate(emails_relevantes):
        contexto += f"--- E-mail {i+1} ---\n"
        contexto += f"De: {email.get('de', 'N/A')}\n"
        contexto += f"Para: {email.get('para', 'N/A')}\n"
        contexto += f"Assunto: {email.get('assunto', 'N/A')}\n\n"
        contexto += f"{email.get('corpo', '')}\n"
        contexto += "---------------------\n\n"
        
    # Inicializa o modelo generativo do Google
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Você é um auditor investigativo da Dunder Mifflin. Sua tarefa é analisar os e-mails abaixo, enviados por Michael Scott,
    e determinar se eles contêm evidências de uma conspiração ou plano contra Toby Flenderson.

    Analise o tom, as palavras usadas e o contexto. Justifique sua resposta final citando trechos específicos dos e-mails.

    E-mails para análise:
    {contexto}

    Análise e Conclusão:
    """
    
    response = model.generate_content(prompt)
    
    return response.text

# Exemplo de uso
if __name__ == '__main__':
    print("Iniciando verificação de conspiração com o Google AI SDK...")
    resultado_analise = verificar_conspiracao()
    print("\n--- Relatório de Análise de Conspiração ---")
    print(resultado_analise)
    print("------------------------------------------")
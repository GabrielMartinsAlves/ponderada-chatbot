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


def analisar_transacoes_complexas(caminho_transacoes, caminho_politica, caminho_emails):
    """
    Analisa fraudes que SÓ PODEM SER DESCOBERTAS COM CONTEXTO DE COMUNICAÇÃO.

    Fluxo:
    1. Primeiro, analisa TODOS os e-mails para identificar padrões suspeitos
       (conluios, combinações de desvio de verba, conspirações)
    2. Depois, busca transações relacionadas aos funcionários/temas suspeitos
    3. Cruza as informações para identificar fraudes contextuais

    Este detector NÃO verifica violações diretas - isso é trabalho do detector simples.
    """
    transacoes = ler_transacoes(caminho_transacoes)
    politica = ler_politica(caminho_politica)
    todos_emails = parse_emails(caminho_emails)

    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.1})

    print("[Fraude Complexa] Etapa 1: Analisando e-mails em busca de padrões suspeitos...")

    # ETAPA 1: Analisar e-mails para encontrar comportamentos suspeitos
    # Limitado para testes
    max_emails = 50
    emails_formatados = ""
    for i, email in enumerate(todos_emails[:max_emails]):
        emails_formatados += f"""
E-mail #{i+1}:
De: {email.get('de', 'N/A')}
Para: {email.get('para', 'N/A')}
Assunto: {email.get('assunto', 'N/A')}
Corpo: {email.get('corpo', '')[:300]}
---
"""

    prompt_emails = f"""Você é um investigador forense da Dunder Mifflin.

        TAREFA: Analisar os e-mails abaixo e identificar COMUNICAÇÕES SUSPEITAS que possam indicar:
        - Funcionários combinando fraudes ou desvios de verba
        - Conluio para burlar regras de compliance
        - Discussões sobre esconder gastos ou manipular relatórios
        - Qualquer conspiração financeira

        E-MAILS:
        {emails_formatados}

        POLÍTICA DE COMPLIANCE (para referência):
        {politica}

        INSTRUÇÕES:
        1. Identifique e-mails que indicam comportamento fraudulento ou suspeito
        2. Liste os funcionários envolvidos e o tipo de fraude suspeita
        3. Se não houver nada suspeito, responda: "Nenhuma comunicação suspeita identificada."

        FORMATO DE RESPOSTA (se houver suspeitas):
        - Funcionários: [nomes]
        - Tipo de fraude suspeita: [descrição]
        - Evidência: [trecho do e-mail]

        ANÁLISE:
    """

    try:
        response = model.generate_content(prompt_emails)
        analise_emails = response.text.strip()
    except Exception as e:
        return [{"erro": f"Erro ao analisar e-mails: {e}"}]

    if "Nenhuma comunicação suspeita identificada." in analise_emails:
        print("[Fraude Complexa] Nenhuma comunicação suspeita encontrada nos e-mails.")
        return []

    print("[Fraude Complexa] Etapa 2: Buscando transações relacionadas às suspeitas...")

    # ETAPA 2: Com base nas suspeitas, buscar transações relacionadas
    # Extrai nomes dos funcionários mencionados na análise
    funcionarios_suspeitos = set()
    for transacao in transacoes:
        nome = transacao['funcionario'].lower()
        if nome in analise_emails.lower():
            funcionarios_suspeitos.add(transacao['funcionario'])

    if not funcionarios_suspeitos:
        print("[Fraude Complexa] Não foi possível vincular suspeitas a transações.")
        return [{
            "tipo": "Comunicação Suspeita (sem vínculo a transações)",
            "analise_emails": analise_emails,
            "transacoes_vinculadas": []
        }]

    # Filtra transações dos funcionários suspeitos
    transacoes_suspeitas = [t for t in transacoes if t['funcionario'] in funcionarios_suspeitos]

    if not transacoes_suspeitas:
        return [{
            "tipo": "Comunicação Suspeita (sem transações encontradas)",
            "analise_emails": analise_emails,
            "transacoes_vinculadas": []
        }]

    # Formata transações para análise final (limitado para testes)
    transacoes_formatadas = ""
    for t in transacoes_suspeitas[:50]:
        transacoes_formatadas += f"ID: {t['id_transacao']} | {t['funcionario']} | ${t['valor']} | {t['descricao']}\n"

    print(f"[Fraude Complexa] Etapa 3: Analisando {min(len(transacoes_suspeitas), 50)} transações de funcionários suspeitos...")

    # ETAPA 3: Análise final cruzando e-mails + transações
    prompt_final = f"""Você é um auditor forense da Dunder Mifflin.

        CONTEXTO: Foram identificadas comunicações suspeitas nos e-mails da empresa.

        ANÁLISE DOS E-MAILS:
        {analise_emails}

        TRANSAÇÕES DOS FUNCIONÁRIOS MENCIONADOS:
        {transacoes_formatadas}

        POLÍTICA DE COMPLIANCE:
        {politica}

        TAREFA: Cruze as informações e identifique transações que, COM BASE NAS COMUNICAÇÕES,
        representam fraudes ou desvios de verba.

        IMPORTANTE: Estas são fraudes que SÓ PODEM SER DESCOBERTAS com o contexto dos e-mails.
        (Transações que parecem normais isoladamente, mas são fraudulentas considerando as comunicações)

        RELATÓRIO FINAL:
    """

    try:
        response = model.generate_content(prompt_final)
        resultado_final = response.text.strip()
    except Exception as e:
        return [{"erro": f"Erro na análise final: {e}"}]

    return [{
        "tipo": "Fraude Contextual Identificada",
        "analise_emails": analise_emails,
        "funcionarios_suspeitos": list(funcionarios_suspeitos),
        "relatorio_final": resultado_final
    }]


if __name__ == '__main__':
    suspeitas = analisar_transacoes_complexas(
        "documents/transacoes_bancarias.csv",
        "documents/politica_compliance.txt",
        "documents/emails_internos.txt"
    )

    print("\n--- Relatório de Fraudes Complexas (Contextuais) ---")
    if not suspeitas:
        print("Nenhuma fraude contextual foi identificada.")
    else:
        for s in suspeitas:
            if "erro" in s:
                print(f"Erro: {s['erro']}")
            else:
                print(f"\nTipo: {s.get('tipo', 'N/A')}")
                print(f"\nAnálise dos E-mails:\n{s.get('analise_emails', 'N/A')}")
                print(f"\nFuncionários Suspeitos: {s.get('funcionarios_suspeitos', [])}")
                print(f"\nRelatório Final:\n{s.get('relatorio_final', 'N/A')}")

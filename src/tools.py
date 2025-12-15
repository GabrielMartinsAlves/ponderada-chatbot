import os
from src.compliance_chatbot import criar_chatbot_compliance, perguntar_ao_chatbot
from src.conspiracy_detector import verificar_conspiracao
from src.fraud_detector_simple import analisar_transacoes_simples
from src.fraud_detector_complex import analisar_transacoes_complexas

# Ensure the chatbot is initialized
caminho_politica = "documents/politica_compliance.txt"
if os.path.exists(caminho_politica):
    criar_chatbot_compliance(caminho_politica)

def compliance_tool(pergunta: str) -> str:
    """
        Responde a perguntas sobre a política de compliance da empresa.
        Use esta ferramenta quando o usuário tiver dúvidas sobre regras, diretrizes ou políticas internas.

        Args:
            pergunta: A pergunta do usuário sobre compliance.
    """
    try:
        return perguntar_ao_chatbot(pergunta)
    except Exception as e:
        return f"Erro ao consultar o chatbot de compliance: {str(e)}"

def conspiracy_tool() -> str:
    """
        Analisa e-mails internos em busca de evidências de conspiração contra Toby Flenderson.
        Use esta ferramenta quando o usuário pedir para investigar conspirações ou tramas.
    """
    try:
        caminho_emails = "documents/emails_internos.txt"
        return verificar_conspiracao(caminho_emails)
    except Exception as e:
        return f"Erro ao verificar conspiração: {str(e)}"

def simple_fraud_tool() -> str:
    """
        Analisa transações bancárias em busca de violações DIRETAS da política de compliance.
        Use esta ferramenta para verificar transações que, POR SI SÓ, quebram regras
        (ex: valores acima do limite, categorias proibidas, fornecedores não autorizados).
    """
    try:
        caminho_transacoes = "documents/transacoes_bancarias.csv"
        caminho_politica = "documents/politica_compliance.txt"
        violacoes = analisar_transacoes_simples(caminho_transacoes, caminho_politica)

        if not violacoes:
            return "Nenhuma violação direta de compliance foi detectada nas transações."

        relatorio = f"Foram encontrados {len(violacoes)} lotes com violações diretas:\n\n"
        for v in violacoes:
            relatorio += f"--- Lote {v['batch']} ---\n{v['justificativa_ia']}\n\n"
        return relatorio
    except Exception as e:
        return f"Erro ao analisar fraudes simples: {str(e)}"

def complex_fraud_tool() -> str:
    """
        Realiza uma análise forense que CRUZA e-mails com transações para descobrir fraudes contextuais.
        Use esta ferramenta para identificar funcionários combinando fraudes, desvios de verba,
        ou conspirações que só podem ser descobertas analisando as comunicações internas.
    """
    try:
        caminho_transacoes = "documents/transacoes_bancarias.csv"
        caminho_politica = "documents/politica_compliance.txt"
        caminho_emails = "documents/emails_internos.txt"

        suspeitas = analisar_transacoes_complexas(caminho_transacoes, caminho_politica, caminho_emails)

        if not suspeitas:
            return "Nenhuma fraude contextual foi identificada nos e-mails e transações."

        relatorio = "=== RELATÓRIO DE FRAUDES CONTEXTUAIS ===\n\n"
        for s in suspeitas:
            if "erro" in s:
                relatorio += f"Erro: {s['erro']}\n"
            else:
                relatorio += f"Tipo: {s.get('tipo', 'N/A')}\n\n"
                relatorio += f"Análise dos E-mails:\n{s.get('analise_emails', 'N/A')}\n\n"
                if s.get('funcionarios_suspeitos'):
                    relatorio += f"Funcionários Suspeitos: {', '.join(s['funcionarios_suspeitos'])}\n\n"
                relatorio += f"Relatório Final:\n{s.get('relatorio_final', 'N/A')}\n"
        return relatorio
    except Exception as e:
        return f"Erro ao analisar fraudes complexas: {str(e)}"


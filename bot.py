import os
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from duckduckgo_search import DDGS
from google import genai
from google.genai import types

# -------------------------------------------------------------
# 1. Configurações e Variáveis de Ambiente
# -------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "2051744073")

if not GEMINI_API_KEY:
    print("ERRO: Variável GEMINI_API_KEY não definida.")
    sys.exit(1)

if not TELEGRAM_BOT_TOKEN:
    print("ERRO: Variável TELEGRAM_BOT_TOKEN não definida.")
    sys.exit(1)


# -------------------------------------------------------------
# 2. Busca na Web com DuckDuckGo
# -------------------------------------------------------------
def buscar_concursos_web():
    """
    Realiza buscas estruturadas na web via DuckDuckGo com termos específicos
    para Piauí, Teresina, Nordeste e Federais/Nacionais de TI.
    """
    consultas = [
        'concurso TI Piauí 2026 2027 "tecnologia da informação"',
        'concurso Teresina TI "analista de sistemas" OR "técnico em informática"',
        'concurso aberto previsto "tecnologia da informação" Piauí',
        'concurso TI Nordeste 2026 edital inscrições abertas',
        'concurso federal TI nacional CNU 2026 2027 vagas tecnologia da informação',
    ]

    resultados_totais = []
    urls_vistas = set()

    print("Iniciando pesquisas de concursos na web via DuckDuckGo...")

    try:
        with DDGS() as ddgs:
            for q in consultas:
                try:
                    res = ddgs.text(q, region="br-pt", timelimit="m", max_results=6)
                    for item in res:
                        href = item.get("href") or item.get("link", "")
                        if href and href not in urls_vistas:
                            urls_vistas.add(href)
                            resultados_totais.append({
                                "title": item.get("title", ""),
                                "link": href,
                                "snippet": item.get("body", "") or item.get("snippet", "")
                            })
                except Exception as erro_busca:
                    print(f"Aviso ao consultar termo '{q}': {erro_busca}")
                time.sleep(1)  # Intervalo de cortesia entre consultas
    except Exception as erro_geral:
        print(f"Erro ao inicializar DuckDuckGo: {erro_geral}")

    print(f"Total de resultados únicos coletados na web: {len(resultados_totais)}")
    return resultados_totais


# -------------------------------------------------------------
# 3. Análise e Formatação com o Google Gemini
# -------------------------------------------------------------
def analisar_com_gemini(resultados_busca):
    """
    Submete os resultados reais da web ao Gemini para filtrar rigorosamente
    apenas vagas de TI, remover editais antigos e classificar por prioridade.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    data_hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y")

    prompt = f"""Você é um assistente especializado em MONITORAMENTO DE CONCURSOS PÚBLICOS.

Sua função é analisar EXCLUSIVAMENTE os resultados de busca da web fornecidos abaixo e identificar oportunidades de concursos relevantes para a área de Tecnologia da Informação (TI).

DATA ATUAL: {data_hoje}

════════════════════════════════════
OBJETIVO E REGRAS
════════════════════════════════════
Você funciona como um RADAR DE CONCURSOS.
Seu objetivo é encontrar o maior número possível de oportunidades relevantes de TI sem perder oportunidades por causa da localização.

A prioridade é encontrar oportunidades próximas a Teresina e Piauí, mas concursos de outras regiões e nacionais também devem ser incluídos quando forem relevantes.

NÃO invente informações.
NÃO complete informações usando conhecimento prévio sem evidência dos resultados.
NÃO faça previsões próprias nem transforme possibilidades em informações confirmadas.

Considere uma oportunidade relacionada à Tecnologia da Informação quando os resultados mencionarem explicitamente cargos ou áreas como:
- Tecnologia da Informação / TI
- Analista de TI / Técnico de TI
- Analista de Sistemas / Desenvolvimento de Software / Programador
- Redes de Computadores / Infraestrutura / Segurança da Informação
- Ciência de Dados / Banco de Dados / Inteligência Artificial

PRIORIDADE GEOGRÁFICA:
1. Teresina - PI
2. Outros municípios do Piauí
3. Cidades vizinhas e Nordeste
4. Concursos nacionais / unificados (CNU, federais)
5. Outros estados quando forem vagas relevantes de TI

SITUAÇÃO DO CONCURSO:
Classifique SOMENTE em:
- Inscrições abertas
- Edital publicado
- Em andamento
- Autorizado
- Comissão formada
- Anunciado
- Previsto

DATAS:
A data atual é {data_hoje}.
Se as inscrições terminaram antes de {data_hoje}, NÃO marque como "Inscrições abertas". Se o concurso estiver totalmente encerrado e sem novas etapas/previsões, descarte.

ORGANIZAÇÃO DAS SEÇÕES:
1. INSCRIÇÕES ABERTAS
2. EDITAIS PUBLICADOS / EM ANDAMENTO
3. AUTORIZADOS / COMISSÃO FORMADA
4. ANUNCIADOS / PREVISTOS

FORMATO DE CADA OPORTUNIDADE:
━━━━━━━━━━━━━━━━━━
Nome:
Órgão:
Cargo/Área:
Local:
Prioridade: [ALTA / MÉDIA / NACIONAL / BAIXA]
Situação:
Vagas:
Data importante:
Escolaridade:
Salário:
Link:
Fonte:
━━━━━━━━━━━━━━━━━━

RESUMO FINAL:
RESUMO
Total de oportunidades relevantes: X
Inscrições abertas: X
Editais publicados/em andamento: X
Autorizados/comissão formada: X
Anunciados/previstos: X

Por prioridade:
Alta: X
Média: X
Nacional: X
Baixa: X

Se nenhum concurso atender aos critérios nos resultados:
"Nenhum concurso de TI relevante encontrado nesta busca."

RESULTADOS COLETADOS DA WEB:
{resultados_busca}
"""

    modelos = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-1.5-flash",
    ]

    for modelo in modelos:
        for tentativa in range(1, 4):
            try:
                print(f"Analisando com {modelo} (tentativa {tentativa}/3)...")
                response = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.2),
                )
                if response.text:
                    return response.text
                break
            except Exception as erro:
                msg = str(erro)
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    print(f"Cota cheia em {modelo}, tentando modelo alternativo...")
                    break
                if any(c in msg for c in ("503", "500", "504", "UNAVAILABLE")):
                    espera = 10 * tentativa
                    print(f"Serviço instável no Google, aguardando {espera}s...")
                    time.sleep(espera)
                    continue
                raise

    raise RuntimeError("Nenhum modelo do Gemini respondeu.")


# -------------------------------------------------------------
# 4. Envio ao Telegram em Partes (< 4000 caracteres)
# -------------------------------------------------------------
def enviar_para_telegram(texto):
    """
    Divide a mensagem em blocos de até 4000 caracteres (limite do Telegram)
    e despacha para o Chat ID configurado.
    """
    limite = 4000
    partes = [texto[i:i + limite] for i in range(0, len(texto), limite)]
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    print(f"Enviando {len(partes)} mensagem(ns) ao Telegram (Chat ID: {TELEGRAM_CHAT_ID})...")

    for idx, parte in enumerate(partes, 1):
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": parte,
            "disable_web_page_preview": True
        }
        res = requests.post(url, json=payload, timeout=25)
        if res.status_code != 200:
            print(f"Aviso ao enviar parte {idx}: {res.text}")
        else:
            print(f"Parte {idx}/{len(partes)} entregue com sucesso!")


# -------------------------------------------------------------
# 5. Ponto de Entrada Principal
# -------------------------------------------------------------
def main():
    try:
        resultados = buscar_concursos_web()
        if not resultados:
            print("Nenhum resultado capturado na web.")
            return

        mensagem = analisar_com_gemini(resultados)
        if not mensagem:
            print("Nenhuma mensagem formatada pelo Gemini.")
            return

        enviar_para_telegram(mensagem)
        print("Execução finalizada com êxito!")
    except Exception as e:
        print(f"Erro durante a execução do bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

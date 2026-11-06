import os
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
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
# 2. Coleta de Oportunidades via Google News RSS (100% Livre de Bloqueios)
# -------------------------------------------------------------
def buscar_noticias_concursos():
    """
    Coleta notícias e editais em tempo real direto dos feeds RSS do Google News.
    Essa abordagem funciona com 100% de estabilidade no GitHub Actions (sem bloqueio de IP).
    """
    consultas = [
        "concurso TI Piaui",
        "concurso TI Teresina",
        "concurso analista sistemas Piaui",
        "concurso tecnico informatica Piaui",
        "concurso tecnologia da informacao Piaui",
        "concurso TI Maranhao Ceara Nordeste",
        "concurso CNU bloco tecnologia da informacao",
        "concurso TI tribunal TRT TRE TRF",
        "concurso federal TI vagas",
        "concurso aberto tecnologia da informacao 2026 2027",
    ]

    noticias = []
    links_vistos = set()

    print("Iniciando varredura de concursos em tempo real (Google News Engine)...")

    for termo in consultas:
        url = (
            f"https://news.google.com/rss/search?"
            f"q={urllib.parse.quote(termo)}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        )
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resposta:
                conteudo_xml = resposta.read()
                raiz = ET.fromstring(conteudo_xml)

                encontrados_nesta_busca = 0
                for item in raiz.findall(".//item")[:10]:
                    titulo = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                    descricao = item.find("description").text if item.find("description") is not None else ""

                    if link and link not in links_vistos:
                        links_vistos.add(link)
                        noticias.append({
                            "termo_pesquisa": termo,
                            "titulo": titulo,
                            "link": link,
                            "data_publicacao": pub_date,
                            "resumo": descricao
                        })
                        encontrados_nesta_busca += 1

                print(f"Termo: '{termo}' -> {encontrados_nesta_busca} oportunidades coletadas.")
        except Exception as erro:
            print(f"Aviso ao consultar '{termo}': {erro}")
        time.sleep(0.5)

    print(f"\nTotal de notícias e editais únicos coletados: {len(noticias)}")
    return noticias


# -------------------------------------------------------------
# 3. Análise, Filtragem e Formatação com o Google Gemini
# -------------------------------------------------------------
def analisar_com_gemini(noticias):
    client = genai.Client(api_key=GEMINI_API_KEY)
    data_hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y")

    prompt = f"""Você é um assistente especializado em MONITORAMENTO DE CONCURSOS PÚBLICOS.

Sua missão é analisar as notícias, editais e publicações recentes fornecidas abaixo e identificar oportunidades de concursos relevantes para a área de Tecnologia da Informação (TI).

DATA ATUAL: {data_hoje}

════════════════════════════════════
OBJETIVO E REGRAS DE FILTRO
════════════════════════════════════
Você funciona como um RADAR DE CONCURSOS.
Seu objetivo é encontrar o maior número possível de oportunidades de TI sem perder oportunidades por causa da localização.

A prioridade máxima é destacar oportunidades em Teresina e no Piauí, mas concursos do Nordeste e Concursos Nacionais/Federais DEVEM ser incluídos com destaque se tiverem vagas de TI.

NÃO invente informações.
NÃO faça previsões próprias nem transforme possibilidades em informações confirmadas.

Considere uma oportunidade de TI quando os resultados mencionarem cargos ou áreas como:
- Tecnologia da Informação / TI
- Analista de TI / Técnico de TI
- Analista de Sistemas / Engenharia de Software / Desenvolvedor / Programador
- Redes / Infraestrutura / Segurança da Informação / Suporte
- Ciência de Dados / Banco de Dados / Inteligência Artificial

PRIORIDADE GEOGRÁFICA:
1. ALTA: Teresina - PI, outros municípios do Piauí e estados vizinhos imediatos (ex: Maranhão, Ceará).
2. MÉDIA: Outros estados do Nordeste.
3. NACIONAL: Concursos federais, unificados (CNU), tribunais federais, bancos e órgãos nacionais.
4. BAIXA: Oportunidades relevantes em outros estados distantes.

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
Se as inscrições terminaram antes de {data_hoje}, NÃO marque como "Inscrições abertas". Se o concurso estiver totalmente encerrado, descarte.

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

Se nenhuma oportunidade de TI for identificada:
"Nenhum concurso de TI relevante encontrado nesta busca."

NOTÍCIAS E PUBLICAÇÕES COLETADAS:
{noticias}
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
        noticias = buscar_noticias_concursos()
        if not noticias:
            print("Nenhuma notícia capturada na web.")
            return

        mensagem = analisar_com_gemini(noticias)
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

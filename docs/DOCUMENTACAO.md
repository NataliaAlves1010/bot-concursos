# 📖 Documentação Completa e Definitiva: Bot Radar de Concursos TI

---

## 📌 1. Visão Geral do Projeto

Este projeto é um sistema autônomo e gratuito de monitoramento de concursos públicos com foco em **Tecnologia da Informação (TI)**, especialmente voltado para **Teresina**, **Piauí**, **Nordeste** e **Concursos Nacionais/Federais**.

O bot substituiu um fluxo complexo do n8n que demandava servidor 24h ligado e serviços pagos como o Tavily, migrando para uma arquitetura **100% Serverless no GitHub Actions com custo R$ 0,00**.

---

## 🏗️ 2. Arquitetura da Solução

```
[GitHub Actions (Cron: 07:55 BRT - Seg/Qua/Sex)]
                      │
                      ▼
[Coleta em Tempo Real via Google News RSS (10 Consultas Estratégicas)]
                      │
                      ▼
[Google Gemini 3.8 Flash (Filtragem Rigorosa de TI & Deduplicação)]
                      │
                      ▼
[Fatiamento em Blocos de até 4.000 Caracteres]
                      │
                      ▼
[Disparo via Telegram Bot API -> Chat ID do Usuário]
```

### 💡 Por que esta arquitetura é superior?
1. **Zero Custo de Hospedagem:** O GitHub Actions roda em containers efêmeros (menos de 25 segundos por execução). Gasta menos de 5 minutos por mês dos 2.000 minutos gratuitos mensais do GitHub.
2. **Zero Custo de Busca:** O motor Google News RSS é aberto, sem limite de requisições, sem chaves de API e imune a bloqueios de bots e CAPTCHAs que afetam scrapers convencionais.
3. **Inteligência com Gemini 3.8 Flash:** Processa dezenas de matérias simultaneamente, descartando editais encerrados e aplicando prioridade geográfica.
4. **Pontualidade:** O agendamento às `10:55 UTC (07:55 BRT)` evita o congestionamento da fila de hora cheia do GitHub Actions, garantindo entrega perto das 08h da manhã.

---

## 📂 3. Estrutura do Repositório

```
bot-concursos/
├── .github/
│   └── workflows/
│       └── concursos.yml   # Agendador Cron e orquestração na nuvem
├── bot.py                  # Script principal em Python
├── requirements.txt        # Dependências mínimas necessárias
└── README.md               # Instruções rápidas do repositório
```

---

## 🐍 4. Explicação Linha por Linha de `bot.py`

### 4.1. Importação de Módulos (Linhas 1 a 11)
```python
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
```
* `os` / `sys`: Leitura de credenciais do sistema e controle de saída com código de status.
* `time`: Pausas preventivas entre requisições HTTP para boa convivência de rede.
* `urllib.request` / `urllib.parse` / `xml.etree.ElementTree`: Módulos nativos do Python usados para consultar e decodificar feeds RSS XML do Google News sem dependências pesadas de terceiros.
* `datetime` / `ZoneInfo`: Manipulação de data e hora respeitando o fuso horário oficial de Brasília (`America/Sao_Paulo`).
* `requests`: Envio das mensagens formatadas para a API REST do Telegram.
* `google.genai` / `types`: SDK oficial mais recente do Google GenAI para comunicação com os modelos Gemini 3.x.

---

### 4.2. Variáveis de Ambiente e Validações (Linhas 16 a 28)
```python
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "2051744073")

if not GEMINI_API_KEY:
    print("ERRO: Variável GEMINI_API_KEY não definida.")
    sys.exit(1)

if not TELEGRAM_BOT_TOKEN:
    print("ERRO: Variável TELEGRAM_BOT_TOKEN não definida.")
    sys.exit(1)
```
* Lê com segurança os segredos injetados pelo GitHub Actions.
* Caso falte alguma chave, encerra o programa imediatamente com código de erro `1`, alertando no console do GitHub Actions.

---

### 4.3. Motor de Busca de Notícias (`buscar_noticias_concursos`, Linhas 34 a 94)
```python
def buscar_noticias_concursos():
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
```
* Realiza 10 buscas estruturadas cobrindo desde Teresina até concursos unificados e tribunais federais.
* Constrói URLs RSS dinâmicas com parâmetros de geolocalização brasileira (`hl=pt-BR&gl=BR&ceid=BR:pt-419`).
* Realiza a leitura dos elementos XML `<title>`, `<link>`, `<pubDate>` e `<description>`.
* Utiliza um conjunto (`set`) de `links_vistos` para eliminar matérias duplicadas antes de entregar ao modelo, economizando tokens e tempo de processamento.

---

### 4.4. Inteligência e Filtragem com Gemini (`analisar_com_gemini`, Linhas 99 a 209)
* **Prompt Especializado:** Instruções detalhadas que atuam como um "Radar de Concursos".
  * Exige relacionamento explícito com cargos de TI (Analista de Sistemas, Técnico de TI, Segurança da Informação, Dados, Infraestrutura, etc.).
  * Impede alucinações e proíbe transformar previsões em editais confirmados.
  * Define prioridades geográficas claras (Alta: Teresina/PI; Média: Nordeste; Nacional: Federais/CNU).
  * Exige descarte de concursos cujo período de inscrição já tenha expirado em relação à data atual.
* **Resiliência e Fallback entre Modelos:**
```python
    modelos = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]
```
* Faz até 3 tentativas por modelo. Se receber erro de descontinuação (`404 NOT_FOUND`) ou cota esgotada (`429 RESOURCE_EXHAUSTED`), passa automaticamente para o próximo modelo sem quebrar a execução.

---

### 4.5. Envio ao Telegram (`enviar_para_telegram`, Linhas 214 a 237)
```python
def enviar_para_telegram(texto):
    limite = 4000
    partes = [texto[i:i + limite] for i in range(0, len(texto), limite)]
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
```
* O Telegram rejeita mensagens com mais de 4.096 caracteres. O código fatia a mensagem com uma margem de segurança de 4.000 caracteres por bloco.
* Configura `disable_web_page_preview: True` para evitar que banners gigantes de notícias poluam a leitura no Telegram.

---

### 4.6. Execução Principal (`main`, Linhas 242 a 267)
* Orquestra o fluxo de ponta a ponta dentro de um bloco `try...except`.
* Finaliza com `if __name__ == "__main__": main()`.

---

## ⚙️ 5. Explicação de `.github/workflows/concursos.yml`

```yaml
name: Monitor Concursos TI

on:
  schedule:
    # 10:55 UTC = 07:55 Horário de Brasília (UTC-3)
    # Segundas (1), Quartas (3) e Sextas (5)
    - cron: '55 10 * * 1,3,5'
  workflow_dispatch: # Permite disparar manualmente pelo botão "Run workflow" no GitHub

jobs:
  executar-radar:
    runs-on: ubuntu-latest

    steps:
      - name: Baixar o código do repositório
        uses: actions/checkout@v4

      - name: Configurar o Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Instalar dependências
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Executar o bot
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python bot.py
```

* **Gatilho Cron:** Programado para `55 10 * * 1,3,5` (segundas, quartas e sextas às 07:55 BRT). Isso evita atrasos comuns nos horários de pico do GitHub Actions.
* **Workflow Dispatch:** Permite executar o bot a qualquer momento pelo botão "Run workflow" no navegador.
* **Segurança dos Secrets:** As chaves de acesso são injetadas em memória na máquina virtual temporária, sem nunca ficarem expostas no código público.

---

## 🔑 6. Configuração dos Segredos no GitHub

Para replicar ou manter o repositório, basta cadastrar os 3 secrets em:
**Settings** > **Secrets and variables** > **Actions** > **New repository secret**:

| Nome do Secret | Descrição | Onde Obter |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Chave de acesso à API do Gemini | [Google AI Studio](https://aistudio.google.com/) |
| `TELEGRAM_BOT_TOKEN` | Token de autenticação do bot | BotFather no Telegram (`/newbot` ou `/token`) |
| `TELEGRAM_CHAT_ID` | Identificador do chat ou canal | `2051744073` (ou use bots como `@userinfobot`) |

---

## 📊 7. Tabela de Custos e Limites

| Recurso | Fornecedor | Plano | Custo | Limite Utilizado |
| :--- | :--- | :--- | :--- | :--- |
| **Execução Serverless** | GitHub Actions | Free | R$ 0,00 | ~5 min / 2.000 min mensais |
| **Modelo de Linguagem** | Google Gemini 3.8 Flash | Free Tier | R$ 0,00 | 1 requisição / dia |
| **Busca de Notícias** | Google News RSS | Público | R$ 0,00 | Ilimitado |
| **Disparo de Mensagens**| Telegram Bot API | Free | R$ 0,00 | Ilimitado |

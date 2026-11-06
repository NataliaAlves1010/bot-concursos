# 🤖 Bot Radar de Concursos TI (Piauí / Nordeste / Nacional)

Sistema automatizado de monitoramento de concursos públicos com foco em **Tecnologia da Informação (TI)**, priorizando **Teresina**, **Piauí**, **Nordeste** e **Concursos Federais/Nacionais**.

---

## ⏰ Agendamento e Execução

O bot opera de forma 100% Serverless no **GitHub Actions** toda:
- **Segunda-feira às 07:55** (Horário de Brasília)
- **Quarta-feira às 07:55** (Horário de Brasília)
- **Sexta-feira às 07:55** (Horário de Brasília)

> *Nota: O agendamento é configurado para as 07:55 (`cron: 55 10 * * 1,3,5`) propositalmente para evitar as filas de espera que ocorrem nos horários em ponto (`:00`) no GitHub Actions, garantindo que os concursos cheguem pontualmente ao Telegram por volta das 08h.*

---

## 🏗️ Arquitetura

```
[GitHub Actions (Cron / Manual)]
               │
               ▼
[Coleta em Tempo Real via Google News RSS (10 termos estratégicos)]
               │
               ▼
[Google Gemini 3.8 Flash (Filtragem rigorosa de TI e deduplicação)]
               │
               ▼
[Telegram Bot API (Fatiamento em blocos < 4000 caracteres)]
```

- **Custo Total:** **R$ 0,00** (GitHub Actions Free + Google News RSS aberto + Gemini Free Tier + Telegram Bot API).
- **Sem Servidor 24h:** O container roda em menos de 25 segundos e desliga automaticamente.

---

## 🔑 Configuração dos Secrets no GitHub

No repositório do GitHub, vá em **Settings** > **Secrets and variables** > **Actions** e adicione as 3 variáveis:

| Secret | Descrição |
| :--- | :--- |
| `GEMINI_API_KEY` | Chave gratuita gerada no [Google AI Studio](https://aistudio.google.com/) |
| `TELEGRAM_BOT_TOKEN` | Token do bot gerado pelo BotFather no Telegram |
| `TELEGRAM_CHAT_ID` | Identificador do chat ou canal para receber as mensagens |

---

## 🧪 Teste Manual

1. Acesse o seu repositório no GitHub.
2. Clique na aba **Actions** > **Monitor Concursos TI**.
3. Clique no botão **Run workflow** e selecione a branch `master`.
4. Em cerca de 20 segundos o relatório completo chegará no seu Telegram.

---

## 📚 Documentação Técnica Completa

Para a explicação linha por linha de todo o código, arquitetura de rede e fluxo de fallbacks:
👉 Consulte [`docs/DOCUMENTACAO.md`](docs/DOCUMENTACAO.md).

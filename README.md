# 🤖 Bot Radar de Concursos TI (Piauí / Nordeste / Nacional)

Bot automatizado que consulta páginas públicas oficiais de concursos, usa o **Google Gemini** para resumir oportunidades de Tecnologia da Informação (TI) e envia o resultado pelo **Telegram**. O bot não usa Google Search Grounding: a busca é feita pela coleta direta de páginas oficiais selecionadas.

## Fontes consultadas

- SEAD e Governo do Piauí
- COPESE/UFPI, IFPI e NUCEPE/UESPI
- Páginas do Ministério da Gestão e da Inovação em Serviços Públicos (MGI) sobre autorizações e CPNU
- Bancas organizadoras: FGV, Cebraspe, FCC, Instituto AOCP, IDECAN, IBFC, Vunesp e Quadrix

A coleta é limitada a essas páginas e pode não encontrar todos os concursos do Brasil. Os resultados devem ser conferidos no edital oficial. A geração de texto usa a cota gratuita disponível para o Gemini; ela continua sujeita aos limites de uso da conta.

## ⏰ Agendamento
Executado automaticamente pelo **GitHub Actions** toda:
- Segunda-feira às 08:00 (Horário de Brasília)
- Quarta-feira às 08:00 (Horário de Brasília)
- Sexta-feira às 08:00 (Horário de Brasília)

---

## 🚀 Como subir para o GitHub

1. Crie um novo repositório **privado** no [GitHub](https://github.com/new).
2. No seu terminal, dentro desta pasta (`c:\Users\alves\code\bot-concursos-ti`):
   ```bash
   git init
   git add .
   git commit -m "feat: radar de concursos ti"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
   git push -u origin main
   ```

---

## 🔑 Configurar os Secrets no GitHub

No repositório que você criou:
1. Vá em **Settings** > **Secrets and variables** > **Actions**.
2. Clique em **New repository secret** e adicione as seguintes variáveis:

| Nome do Secret | Valor / Descrição |
| :--- | :--- |
| `GEMINI_API_KEY` | Sua chave do Google AI Studio (Gemini) |
| `TELEGRAM_BOT_TOKEN` | Token do seu bot do Telegram (BotFather) |
| `TELEGRAM_CHAT_ID` | `2051744073` (ou o ID do chat/canal que preferir) |

---

## 🧪 Como testar na hora (sem esperar as 08:00)

1. No seu repositório no GitHub, clique na aba **Actions**.
2. No menu lateral esquerdo, clique em **Monitor Concursos TI**.
3. Clique no botão **Run workflow** e selecione a branch `main`.
4. A execução consulta as fontes configuradas, resume o conteúdo disponível e envia a mensagem ao Telegram. O tempo depende da disponibilidade dos sites oficiais.

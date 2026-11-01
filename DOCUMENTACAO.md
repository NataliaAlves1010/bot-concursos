# Documentação do Bot Radar de Concursos TI

## Como funciona

1. O GitHub Actions executa o bot às segundas, quartas e sextas às 08:00, horário de Brasília. Também é possível iniciar uma execução manual na aba **Actions**.
2. O script consulta páginas públicas oficiais da SEAD e do Governo do Piauí, da COPESE/UFPI, do IFPI, do NUCEPE/UESPI e páginas do MGI sobre concursos federais e CPNU.
3. O bot extrai o texto das páginas e, quando encontra links internos relacionados a concursos ou editais, consulta até dois detalhes por fonte.
4. O Gemini 3.8 Flash resume somente o material coletado. A chamada não ativa Google Search Grounding.
5. O resultado é dividido em mensagens e enviado ao Telegram.

## Fontes monitoradas

As URLs ficam na lista `FONTES_OFICIAIS` em `bot.py`. A coleta busca primeiro a listagem de cada fonte e abre um número limitado de páginas internas. Os sites podem mudar sua estrutura, ficar indisponíveis ou publicar editais em links que o coletor não reconhece.

O conjunto é intencionalmente limitado, com foco no Piauí e em páginas federais do MGI. Ele não substitui uma pesquisa abrangente em todos os órgãos e estados. Confira oportunidades e prazos sempre no edital oficial; o Gemini não deve preencher dados que não estejam presentes no texto coletado.

## Uso da API do Gemini

O script usa `gemini-3.8-flash` apenas para geração de texto e não envia a ferramenta `google_search`. Isso evita a cobrança/cota específica do Search Grounding. A API gratuita ainda possui limites de uso e pode retornar erros de cota; esses limites são definidos pelo Google e podem mudar.

## Secrets do GitHub

Em **Settings → Secrets and variables → Actions**, configure:

- `GEMINI_API_KEY`: chave da API Gemini.
- `TELEGRAM_BOT_TOKEN`: token do bot criado pelo BotFather.
- `TELEGRAM_CHAT_ID`: identificador do chat ou canal de destino.

Não coloque esses valores no código nem em arquivos versionados.

## Dependências

As dependências estão em `requirements.txt`:

- `requests`: acesso às páginas públicas e à API do Telegram.
- `google-genai`: chamada ao Gemini.
- `beautifulsoup4`: extração do texto e dos links das páginas HTML.

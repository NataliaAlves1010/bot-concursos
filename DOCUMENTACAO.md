# 📖 Documentação Detalhada: Bot Radar de Concursos TI

Esta documentação explica a arquitetura e **cada linha de código** do bot que substitui o workflow do n8n por uma solução nativa em Python rodando no GitHub Actions com custo R$ 0,00.

---

## 🏗️ 1. Visão Geral da Arquitetura

O bot opera em um modelo **Serverless On-Demand** (sem servidor ligado 24h):
1. **GitHub Actions (Gatilho Cron):** Toda segunda, quarta e sexta às 08:00 (Brasília), o GitHub liga um container Ubuntu temporário.
2. **Execução do Script (`bot.py`):**
   * Configura o cliente do Google Gemini.
   * Aciona a ferramenta nativa de **Google Search Grounding**, realizando a busca na web em tempo real.
   * Filtra, sintetiza e formata os editais de TI com prioridade para Teresina/PI e Concursos Nacionais.
   * Divide o resultado em pedaços de no máximo 4.000 caracteres (evitando limite do Telegram).
   * Dispara as mensagens via HTTP POST para a API do Telegram.
3. **Desligamento:** A máquina temporária do GitHub é destruída imediatamente após a execução.

---

## 🐍 2. Explicação Linha por Linha de `bot.py`

### 📦 Seção 1: Importação de Bibliotecas (Linhas 1 a 6)

```python
1: import os
2: import sys
3: from datetime import datetime
4: import requests
5: from google import genai
6: from google.genai import types
```

* **Linha 1 (`import os`):** Importa o módulo do sistema operacional do Python. Usado para ler as variáveis de ambiente com as chaves de API (`os.environ`).
* **Linha 2 (`import sys`):** Permite interagir com o interpretador. Usamos `sys.exit(1)` para abortar o script com código de erro caso falte alguma credencial.
* **Linha 3 (`from datetime import datetime`):** Importa a classe para manipular datas. Usada para injetar a data atual dinamicamente no prompt.
* **Linha 4 (`import requests`):** Biblioteca padrão de requisições HTTP para enviar as mensagens para a API do Telegram.
* **Linha 5 (`from google import genai`):** Importa o SDK oficial do Google GenAI para autenticar e comunicar com o modelo Gemini.
* **Linha 6 (`from google.genai import types`):** Importa as estruturas de dados e tipos do SDK do Google, necessárias para configurar a ferramenta de busca (`types.Tool`, `types.GoogleSearch()`).

---

### ⚙️ Seção 2: Variáveis de Ambiente e Validações (Linhas 8 a 22)

```python
8:  # -------------------------------------------------------------
9:  # Configurações e Variáveis de Ambiente
10: # -------------------------------------------------------------
11: GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
12: TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
13: TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "2051744073")
```

* **Linha 11:** Recupera a chave da API do Gemini injetada pelo GitHub Actions. Se não existir, retorna `None`.
* **Linha 12:** Recupera o token do Bot do Telegram gerado via BotFather.
* **Linha 13:** Recupera o ID do chat/canal do Telegram. Se a variável não for fornecida, assume o valor padrão `"2051744073"`.

```python
15: if not GEMINI_API_KEY:
16:     print("ERRO: Variável GEMINI_API_KEY não definida.")
17:     sys.exit(1)
18: 
19: if not TELEGRAM_BOT_TOKEN:
20:     print("ERRO: Variável TELEGRAM_BOT_TOKEN não definida.")
21:     sys.exit(1)
```

* **Linhas 15 a 21:** Validações de segurança obrigatórias. Se o desenvolvedor esqueceu de cadastrar as chaves no GitHub Secrets, o script interrompe a execução imediatamente com uma mensagem clara no terminal, evitando falhas silenciosas.

---

### 🧠 Seção 3: Função `gerar_radar_concursos()` (Linhas 24 a 142)

```python
24: def gerar_radar_concursos():
25:     """
26:     Usa o Gemini com a ferramenta nativa de Busca do Google (Grounding)
27:     para pesquisar concursos de TI em tempo real na web e formatar o resultado.
28:     """
29:     client = genai.Client(api_key=GEMINI_API_KEY)
30:     data_hoje = datetime.now().strftime("%d/%m/%Y")
```

* **Linha 24:** Define a função principal de inteligência e busca.
* **Linha 29:** Instancia o cliente da API do Google utilizando a chave autenticada.
* **Linha 30:** Obtém o dia atual no formato brasileiro `DD/MM/AAAA` (ex: `12/10/2026`). Isso corrige um problema do workflow original do n8n, onde a data estava travada estaticamente em 04/10/2026.

```python
32:     prompt = f"""Você é um assistente especializado em MONITORAMENTO DE CONCURSOS PÚBLICOS.
33: 
34: Sua função é PESQUISAR NA WEB em tempo real (utilizando o Google Search) e identificar oportunidades de concursos relevantes, principalmente para a área de Tecnologia da Informação (TI).
...
129: """
```

* **Linhas 32 a 129:** Monta uma f-string com as instruções e diretrizes para o Gemini:
  * **Linhas 40-49:** Fornece os termos prioritários de busca no Google (`concursos TI Teresina Piauí`, `analista de sistemas Piauí`, etc.).
  * **Linhas 51-69:** Define o que é considerado oportunidade de TI e proíbe alucinações ("NÃO invente informações", "NÃO faça previsões").
  * **Linhas 70-76:** Define a hierarquia geográfica (Teresina/PI > Cidades próximas > Nordeste > Nacional/CNU > Outros estados).
  * **Linhas 77-90:** Filtra situações válidas (Inscrições abertas, Previsto, etc.) e descarta editais com prazos encerrados antes da data atual (`{data_hoje}`).
  * **Linhas 97-129:** Padroniza a formatação visual das mensagens e do resumo final.

```python
131:     print("Pesquisando na web e analisando com Google Gemini (Search Grounding ativado)...")
132:     
133:     # Ativa a busca nativa do Google no Gemini
134:     response = client.models.generate_content(
135:         model="gemini-3.8-flash",
136:         contents=prompt,
137:         config=types.GenerateContentConfig(
138:             tools=[types.Tool(google_search=types.GoogleSearch())],
139:             temperature=0.2
140:         )
141:     )
142:     return response.text
```

* **Linha 131:** Emite um log no console do GitHub Actions para monitoramento.
* **Linha 134:** Chama a API de geração de conteúdo do Gemini.
* **Linha 135:** Usa o modelo `gemini-3.8-flash`, compatível com a busca na web (Search Grounding).
* **Linha 136:** Envia o prompt com os termos e regras.
* **Linha 137:** Configura os parâmetros avançados da geração.
* **Linha 138 (`tools=[types.Tool(google_search=types.GoogleSearch())]`):** **Linha chave!** É aqui que ativamos o *Google Search Grounding*. Isso instrui o Gemini a não responder apenas com sua memória de treino, mas sim a disparar buscas ativas no Google para coletar informações em tempo real.
* **Linha 139 (`temperature=0.2`):** Reduz a aleatoriedade (criatividade) do modelo para mantê-lo estritamente focado em fatos e dados reais dos editais.
* **Linha 142:** Retorna o texto formatado pelo modelo.

---

### 📱 Seção 4: Função `enviar_para_telegram()` (Linhas 145 a 166)

```python
145: def enviar_para_telegram(texto):
146:     """
147:     Divide a mensagem em blocos de até 4000 caracteres (limite do Telegram)
148:     e envia para o chat configurado.
149:     """
150:     limite = 4000
151:     partes = [texto[i:i + limite] for i in range(0, len(texto), limite)]
152:     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
```

* **Linha 150:** O Telegram impõe um limite rígido de 4.096 caracteres por mensagem. Usamos `4000` como margem segura.
* **Linha 151:** Faz o mesmo que o nó JavaScript do n8n fazia: uma list comprehension fatiando a string em blocos de até 4.000 caracteres.
* **Linha 152:** Monta a URL oficial da API do Telegram para o endpoint `sendMessage`.

```python
154:     print(f"Enviando {len(partes)} parte(s) para o Telegram (Chat ID: {TELEGRAM_CHAT_ID})...")
155: 
156:     for idx, parte in enumerate(partes, 1):
157:         payload = {
158:             "chat_id": TELEGRAM_CHAT_ID,
159:             "text": parte,
160:             "disable_web_page_preview": True
161:         }
162:         res = requests.post(url, json=payload, timeout=25)
163:         if res.status_code != 200:
164:             print(f"Aviso ao enviar parte {idx}: {res.text}")
165:         else:
166:             print(f"Parte {idx}/{len(partes)} enviada com sucesso!")
```

* **Linha 156:** Itera sobre cada pedaço da mensagem com seu respectivo índice.
* **Linhas 157 a 161:** Monta o corpo da requisição JSON:
  * `chat_id`: O destino (usuário ou canal).
  * `text`: O conteúdo do bloco atual.
  * `disable_web_page_preview: True`: Evita que prévias gigantes de links poluam a conversa no Telegram.
* **Linha 162:** Envia a requisição HTTP POST para a API do Telegram com timeout de 25 segundos.
* **Linhas 163 a 166:** Valida a resposta HTTP. Se houver falha, imprime o erro retornado pelo Telegram no log da ação.

---

### 🚀 Seção 5: Orquestração e Ponto de Entrada (Linhas 169 a 183)

```python
169: def main():
170:     try:
171:         conteudo = gerar_radar_concursos()
172:         if not conteudo:
173:             print("Nenhum conteúdo gerado pelo modelo.")
174:             return
175:         enviar_para_telegram(conteudo)
176:         print("Execução finalizada com sucesso!")
177:     except Exception as e:
178:         print(f"Erro durante a execução: {e}")
179:         sys.exit(1)
```

* **Linha 169:** Define a função orquestradora `main`.
* **Linha 170:** Bloco `try...except` para capturar exceções inesperadas (como falhas de conexão de rede ou erros de API).
* **Linha 171:** Chama a geração e pesquisa de concursos.
* **Linha 175:** Dispara o envio das partes para o Telegram.
* **Linhas 177 a 179:** Se algo falhar, exibe a mensagem de erro exata e encerra com código de saída `1` (sinalizando ao GitHub Actions que houve falha para que ele mostre o status vermelho no painel).

```python
182: if __name__ == "__main__":
183:     main()
```

* **Linhas 182 e 183:** Padrão Python idiomático. Garante que a função `main()` só seja disparada quando o arquivo for executado diretamente via linha de comando (`python bot.py`), e não quando importado como módulo em outro arquivo.

---

## ⚙️ 3. Explicação Linha por Linha de `.github/workflows/concursos.yml`

```yaml
1: name: Monitor Concursos TI
```
* **Linha 1:** O nome que aparecerá no painel da aba **Actions** no seu GitHub.

```yaml
3: on:
4:   schedule:
5:     # 11:00 UTC = 08:00 Horário de Brasília (UTC-3)
6:     # Segundas (1), Quartas (3) e Sextas (5)
7:     - cron: '0 11 * * 1,3,5'
8:   workflow_dispatch:
```
* **Linha 3:** Define os eventos disparadores (*triggers*).
* **Linhas 4 a 7 (`schedule` com `cron`):**
  * `0`: Minuto 0.
  * `11`: Hora 11 no relógio UTC. Como o fuso de Brasília é UTC-3, 11h UTC corresponde exatamente às **08:00 da manhã** no Brasil.
  * `* *`: Qualquer dia do mês e qualquer mês.
  * `1,3,5`: Dias da semana (1 = Segunda, 3 = Quarta, 5 = Sexta).
* **Linha 8 (`workflow_dispatch`):** Habilita um botão manual **"Run workflow"** na interface do GitHub para você testar a qualquer momento sem esperar as 08:00.

```yaml
10: jobs:
11:   executar-radar:
12:     runs-on: ubuntu-latest
```
* **Linha 10:** Bloco onde definimos os trabalhos a serem executados.
* **Linha 11:** Nome do job (`executar-radar`).
* **Linha 12:** Especifica o sistema operacional da máquina virtual gratuita que o GitHub fornecerá (a versão mais recente do Ubuntu Linux).

```yaml
14:     steps:
15:       - name: Baixar o código do repositório
16:         uses: actions/checkout@v4
```
* **Linhas 15 e 16:** Usa a action oficial do GitHub para clonar os arquivos do seu repositório para dentro da máquina virtual.

```yaml
18:       - name: Configurar o Python
19:         uses: actions/setup-python@v5
20:         with:
21:           python-version: '3.11'
22:           cache: 'pip'
```
* **Linhas 18 a 22:** Prepara o ambiente Python:
  * `python-version: '3.11'`: Garante uma versão estável e compatível do Python.
  * `cache: 'pip'`: Salva em cache as dependências para as próximas execuções serem ainda mais rápidas (economizando tempo).

```yaml
24:       - name: Instalar dependências
25:         run: |
26:           python -m pip install --upgrade pip
27:           pip install -r requirements.txt
```
* **Linhas 24 a 27:** Atualiza o instalador `pip` e instala as bibliotecas listadas no `requirements.txt` (`requests` e `google-genai`).

```yaml
29:       - name: Executar o bot
30:         env:
31:           GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
32:           TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
33:           TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
34:         run: |
35:           python bot.py
```
* **Linhas 29 a 33:** Injeta com segurança os segredos que você cadastrou no repositório como variáveis de ambiente no container. Nenhuma chave fica exposta no código.
* **Linhas 34 e 35:** Executa o script `bot.py` via terminal. Ao terminar, a máquina é desligada automaticamente.

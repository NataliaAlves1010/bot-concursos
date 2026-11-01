# =============================================================
# 1. IMPORTAÇÃO DE BIBLIOTECAS
# =============================================================

import os
# Importa a biblioteca os, que permite interagir com o sistema
# operacional.
# Neste programa, ela será usada para acessar variáveis de ambiente,
# onde armazenamos as chaves de acesso às APIs.

import sys
# Importa a biblioteca sys, que permite interagir com o interpretador
# Python.
# Aqui, utilizaremos sys.exit(1) para encerrar o programa quando
# ocorrer um erro que impeça sua execução.

from datetime import datetime
# Importa a classe datetime do módulo datetime.
# Ela permite trabalhar com datas e horários.
# Neste código, vamos utilizá-la para obter a data atual.

import requests
# Importa a biblioteca requests, utilizada para realizar requisições HTTP.
# Ela será responsável por enviar mensagens para a API do Telegram.

from google import genai
# Importa o módulo genai da biblioteca oficial do Google.
# Ele permite criar um cliente para se comunicar com a API do Gemini.

from google.genai import types
# Importa os tipos e as configurações disponibilizados pela biblioteca.
# Utilizaremos esses recursos para configurar o modelo e ativar
# a ferramenta de pesquisa Google Search.


# =============================================================
# 2. CONFIGURAÇÕES E VARIÁVEIS DE AMBIENTE
# =============================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# Procura no ambiente do sistema uma variável chamada GEMINI_API_KEY.
# Se ela existir, seu valor será armazenado nessa variável Python.
# Essa chave autoriza o programa a utilizar a API do Gemini.
# Se não existir, o resultado será None.

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# Procura a variável de ambiente TELEGRAM_BOT_TOKEN.
# Ela contém o token de autenticação do bot do Telegram.
# O programa utilizará esse token para enviar mensagens.

TELEGRAM_CHAT_ID = os.environ.get(
    "TELEGRAM_CHAT_ID", "2051744073"
)
# Procura a variável de ambiente TELEGRAM_CHAT_ID.
# O segundo argumento, "2051744073", é um valor padrão.
# Isso significa que, se a variável de ambiente não existir,
# o programa utilizará esse identificador de chat.
# Se ela existir, o valor configurado no ambiente terá prioridade.


# Verifica se a chave do Gemini foi encontrada.
if not GEMINI_API_KEY:
    # Essa condição será verdadeira se a variável estiver vazia
    # ou se seu valor for None.

    print("ERRO: Variável GEMINI_API_KEY não definida.")
    # Exibe uma mensagem explicando o problema no terminal.

    sys.exit(1)
    # Encerra o programa.
    # O número 1 indica que a execução terminou com erro.


# Verifica se o token do Telegram foi encontrado.
if not TELEGRAM_BOT_TOKEN:
    # Se não houver token, não será possível autenticar o bot.

    print("ERRO: Variável TELEGRAM_BOT_TOKEN não definida.")
    # Informa o erro ao usuário.

    sys.exit(1)
    # Interrompe a execução para evitar uma tentativa de envio
    # sem as credenciais necessárias.


# =============================================================
# 3. FUNÇÃO QUE PESQUISA OS CONCURSOS
# =============================================================

def gerar_radar_concursos():
    # Define uma função chamada gerar_radar_concursos.
    # Uma função agrupa instruções que podem ser executadas
    # quando ela é chamada.
    # O objetivo desta função é pesquisar oportunidades de concursos
    # e devolver o texto produzido pelo Gemini.

    """
    Usa o Gemini com a ferramenta nativa de Busca do Google
    para pesquisar concursos de TI na web e formatar o resultado.
    """
    # Este bloco entre aspas triplas é uma docstring.
    # Ela documenta a finalidade da função.
    # Diferentemente dos comentários com #, uma docstring pode ser
    # acessada pela documentação da função.

    client = genai.Client(api_key=GEMINI_API_KEY)
    # Cria um cliente para acessar a API do Gemini.
    # O argumento api_key recebe a chave armazenada anteriormente.
    # O cliente será utilizado para enviar solicitações ao modelo.

    data_hoje = datetime.now().strftime("%d/%m/%Y")
    # datetime.now() obtém a data e o horário locais do computador.
    # strftime("%d/%m/%Y") transforma a data em texto no formato
    # dia/mês/ano.
    # Exemplo: 15/10/2026.
    # Essa data será incluída nas instruções enviadas ao Gemini.
    # Atenção: a data depende do relógio e do fuso horário
    # configurados no ambiente onde o programa está sendo executado.


    # ---------------------------------------------------------
    # 3.1. CRIAÇÃO DO PROMPT
    # ---------------------------------------------------------

    prompt = f"""Você é um assistente especializado em MONITORAMENTO DE CONCURSOS PÚBLICOS.

Sua função é PESQUISAR NA WEB em tempo real (utilizando o Google Search) e identificar oportunidades de concursos relevantes, principalmente para a área de Tecnologia da Informação (TI).

DATA ATUAL:
{data_hoje}

════════════════════════════════════
TERMOS DE PESQUISA PRIORITÁRIOS
════════════════════════════════════
Pesquise especificamente por:
- concursos TI Teresina Piauí
- concursos previstos ou abertos TI Piauí 2026 2027
- "tecnologia da informação" "Teresina" concurso
- "analista de sistemas" concurso Piauí
- "técnico em informática" concurso Piauí
- concursos federais / nacionais TI (com vagas ou lotação no PI ou CNU)

════════════════════════════════════
OBJETIVO E REGRAS
════════════════════════════════════
Você funciona como um RADAR DE CONCURSOS.
Seu objetivo é encontrar o maior número possível de oportunidades relevantes de TI sem perder oportunidades por causa da localização.

A prioridade é encontrar oportunidades próximas a Teresina e Piauí, mas concursos de outras regiões e nacionais também devem ser incluídos quando forem relevantes.

NÃO invente informações.
NÃO complete informações usando conhecimento prévio sem evidência da busca.
NÃO faça previsões próprias.
NÃO transforme possibilidades em informações confirmadas.

Considere uma oportunidade relacionada à Tecnologia da Informação quando as notícias/editais mencionarem explicitamente:
- Tecnologia da Informação / TI
- Analista de TI / Técnico de TI
- Desenvolvimento de Sistemas / Programação
- Infraestrutura / Redes de Computadores / Segurança da Informação
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
Se as inscrições terminaram antes de {data_hoje}, NÃO marque como "Inscrições abertas". Se o concurso estiver totalmente encerrado, descarte.

ORGANIZAÇÃO:
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

Se nenhum concurso atender aos critérios:
"Nenhum concurso de TI relevante encontrado nesta busca."
"""
    # Cria uma string multilinha chamada prompt.
    # O prefixo f antes das aspas permite utilizar f-string.
    # Assim, o Python substitui {data_hoje} pelo valor da variável.
    #
    # O prompt contém as instruções que orientam o Gemini:
    # quais concursos pesquisar, como avaliar as informações,
    # como classificá-las e qual formato utilizar na resposta.
    #
    # Importante: o prompt orienta o comportamento do modelo,
    # mas não garante que todos os concursos existentes sejam encontrados
    # nem que todas as informações retornadas estejam corretas.


    # ---------------------------------------------------------
    # 3.2. EXIBIÇÃO DE UMA MENSAGEM NO TERMINAL
    # ---------------------------------------------------------

    print(
        "Pesquisando na web e analisando com Google Gemini "
        "(Search Grounding ativado)..."
    )
    # Exibe uma mensagem para indicar que a pesquisa está começando.
    # print() mostra informações no terminal.
    # Essa instrução não realiza a pesquisa; apenas informa o usuário.


    # ---------------------------------------------------------
    # 3.3. ENVIO DA SOLICITAÇÃO AO GEMINI
    # ---------------------------------------------------------

    response = client.models.generate_content(
        # Chama o método generate_content do cliente do Gemini.
        # Esse método envia uma solicitação para gerar conteúdo
        # utilizando o modelo escolhido.

        model="gemini-3.8-flash",
        # Define o modelo utilizado.
        # O nome precisa corresponder a um modelo disponível
        # e compatível com a API e com a ferramenta de busca.

        contents=prompt,
        # Envia o prompt criado anteriormente como conteúdo
        # da solicitação.
        # É nesse texto que estão as instruções da pesquisa.

        config=types.GenerateContentConfig(
            # Cria um objeto de configuração para a geração.
            # Nele, podemos definir ferramentas e parâmetros do modelo.

            tools=[
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ],
            # Disponibiliza a ferramenta Google Search ao modelo.
            # Isso permite que o Gemini faça buscas na web durante
            # a geração da resposta, quando necessário.
            #
            # A disponibilidade da ferramenta depende do modelo
            # e da versão da API utilizados.

            temperature=0.2
            # Define a temperatura de geração.
            # Um valor baixo tende a tornar as respostas menos variadas.
            # Aqui, 0.2 favorece respostas mais consistentes.
            # Isso não garante precisão factual nem impede alucinações.
        )
    )
    # O resultado da chamada é armazenado em response.
    # Esse objeto contém os dados devolvidos pela API,
    # incluindo, normalmente, o texto gerado pelo modelo.


    # ---------------------------------------------------------
    # 3.4. RETORNO DO RESULTADO
    # ---------------------------------------------------------

    return response.text
    # Retorna o texto produzido pelo Gemini.
    # return encerra a função e entrega o valor a quem a chamou.
    # Assim, outra parte do programa pode receber esse texto,
    # armazená-lo em uma variável e enviá-lo ao Telegram.


# =============================================================
# 4. FUNÇÃO QUE ENVIA O RESULTADO AO TELEGRAM
# =============================================================

def enviar_para_telegram(texto):
    # Define uma função que recebe um argumento chamado texto.
    # Esse argumento deverá conter a resposta produzida pelo Gemini.
    # A função será responsável por encaminhar o resultado ao Telegram.

    """
    Divide a mensagem em blocos de até 4000 caracteres
    e envia para o chat configurado.
    """
    # Documenta a finalidade da função.


    # ---------------------------------------------------------
    # 4.1. DEFINIÇÃO DO TAMANHO DOS BLOCOS
    # ---------------------------------------------------------

    limite = 4000
    # Define o tamanho máximo pretendido para cada bloco.
    # O Telegram possui limites de tamanho para mensagens.
    # Dividir o conteúdo ajuda a evitar erros quando a resposta
    # do Gemini é muito longa.
    # O limite de 4000 é uma margem conservadora em relação
    # ao limite usual de 4096 caracteres do sendMessage.


    # ---------------------------------------------------------
    # 4.2. DIVISÃO DO TEXTO
    # ---------------------------------------------------------

    partes = [
        texto[i:i + limite]
        for i in range(0, len(texto), limite)
    ]
    # Cria uma lista chamada partes utilizando uma compreensão de lista.
    #
    # len(texto):
    #   Obtém o número total de caracteres do texto.
    #
    # range(0, len(texto), limite):
    #   Gera posições começando em 0, avançando de 4000 em 4000,
    #   até alcançar o final do texto.
    #
    # texto[i:i + limite]:
    #   Extrai uma parte do texto começando na posição i
    #   e terminando antes da posição i + limite.
    #
    # Exemplo:
    # Se texto tiver 8500 caracteres, a lista terá três partes:
    # 4000 caracteres, 4000 caracteres e 500 caracteres.
    #
    # Se texto estiver vazio, a lista também ficará vazia.


    # ---------------------------------------------------------
    # 4.3. MONTAGEM DO ENDEREÇO DA API DO TELEGRAM
    # ---------------------------------------------------------

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )
    # Monta o endereço utilizado para enviar mensagens pelo Telegram.
    # A f-string insere o token do bot na URL.
    #
    # O método sendMessage é um recurso da Bot API do Telegram.
    # O token funciona como uma credencial secreta e não deve
    # ser compartilhado nem publicado em repositórios.


    # ---------------------------------------------------------
    # 4.4. INFORMAÇÃO SOBRE O ENVIO
    # ---------------------------------------------------------

    print(
        f"Enviando {len(partes)} parte(s) para o Telegram "
        f"(Chat ID: {TELEGRAM_CHAT_ID})..."
    )
    # len(partes) informa quantos blocos foram criados.
    # A f-string substitui as expressões entre chaves pelos valores.
    # A mensagem é exibida no terminal para acompanhar a execução.


    # ---------------------------------------------------------
    # 4.5. ENVIO DE CADA PARTE
    # ---------------------------------------------------------

    for idx, parte in enumerate(partes, 1):
        # Percorre a lista partes.
        #
        # enumerate(partes, 1) fornece dois valores a cada repetição:
        # idx  = número da parte, começando em 1;
        # parte = conteúdo do bloco atual.
        #
        # Por exemplo, na primeira repetição:
        # idx será 1 e parte conterá o primeiro bloco.


        payload = {
            # Cria um dicionário com os dados da mensagem.
            # Esse dicionário será enviado à API do Telegram.

            "chat_id": TELEGRAM_CHAT_ID,
            # Identifica o chat, grupo ou canal de destino.
            # O bot precisa ter permissão para enviar mensagens
            # nesse destino.

            "text": parte,
            # Define o conteúdo da mensagem.
            # Aqui, parte é o bloco atual do texto produzido pelo Gemini.

            "disable_web_page_preview": True
            # Solicita que o Telegram não exiba a prévia dos links.
            # Isso deixa a mensagem mais compacta.
        }


        # -----------------------------------------------------
        # 4.6. REQUISIÇÃO HTTP PARA O TELEGRAM
        # -----------------------------------------------------

        res = requests.post(
            url,
            # Endereço da API que receberá a solicitação.

            json=payload,
            # Envia o dicionário payload como JSON.
            # A biblioteca requests serializa os dados para o formato
            # JSON e configura o tipo de conteúdo apropriado.

            timeout=25
            # Define um limite de 25 segundos para a operação.
            # Isso evita que a requisição fique esperando indefinidamente.
        )
        # A resposta HTTP do Telegram fica armazenada em res.
        # Ela contém informações como o código de status e o corpo
        # da resposta da API.


        # -----------------------------------------------------
        # 4.7. VERIFICAÇÃO DO RESULTADO DO ENVIO
        # -----------------------------------------------------

        if res.status_code != 200:
            # Verifica se o código HTTP recebido é diferente de 200.
            # O código 200 normalmente indica que a requisição HTTP
            # foi processada com sucesso.

            print(f"Aviso ao enviar parte {idx}: {res.text}")
            # Se houver outro código, exibe um aviso no terminal.
            # res.text contém o corpo da resposta do servidor,
            # que pode explicar o motivo do problema.

        else:
            # Este bloco é executado quando o código HTTP é 200.

            print(
                f"Parte {idx}/{len(partes)} enviada com sucesso!"
            )
            # Informa qual parte foi aceita pela API.
            #
            # Observação: o código HTTP 200 é um bom sinal,
            # mas a API do Telegram também retorna um campo "ok"
            # no JSON. Verificá-lo seria uma validação adicional.


# =============================================================
# 5. FUNÇÃO PRINCIPAL DO PROGRAMA
# =============================================================

def main():
    # Define a função principal.
    # Ela organiza a sequência geral de execução do programa:
    # pesquisar, verificar o resultado e enviar ao Telegram.


    # ---------------------------------------------------------
    # 5.1. TRATAMENTO DE EXCEÇÕES
    # ---------------------------------------------------------

    try:
        # Inicia um bloco try.
        # O Python tentará executar as instruções dentro dele.
        # Se uma exceção ocorrer, o programa poderá tratá-la
        # no bloco except correspondente.


        # -----------------------------------------------------
        # 5.2. EXECUÇÃO DA PESQUISA
        # -----------------------------------------------------

        conteudo = gerar_radar_concursos()
        # Chama a função que pesquisa os concursos.
        # O valor devolvido pelo return da função é armazenado
        # na variável conteudo.
        #
        # Portanto, conteudo recebe o texto produzido pelo Gemini.


        # -----------------------------------------------------
        # 5.3. VERIFICAÇÃO DO CONTEÚDO
        # -----------------------------------------------------

        if not conteudo:
            # Verifica se conteudo é um valor considerado falso.
            # Isso acontece, por exemplo, se o resultado for None
            # ou uma string vazia.

            print("Nenhum conteúdo gerado pelo modelo.")
            # Informa que não há texto para encaminhar.

            return
            # Encerra a função main imediatamente.
            # Com isso, o programa não chama o Telegram
            # quando não há conteúdo para enviar.


        # -----------------------------------------------------
        # 5.4. ENVIO DO CONTEÚDO
        # -----------------------------------------------------

        enviar_para_telegram(conteudo)
        # Chama a função de envio e passa o texto obtido do Gemini.
        # A função dividirá o texto em partes e enviará cada uma
        # para o chat configurado.


        # -----------------------------------------------------
        # 5.5. MENSAGEM DE CONCLUSÃO
        # -----------------------------------------------------

        print("Execução finalizada com sucesso!")
        # Exibe uma mensagem indicando que o fluxo chegou ao fim
        # sem que uma exceção tenha sido propagada até este bloco.
        #
        # Atenção: no código original, falhas no envio que apenas
        # geram avisos não impedem esta mensagem de aparecer.


    # ---------------------------------------------------------
    # 5.6. CAPTURA DE ERROS
    # ---------------------------------------------------------

    except Exception as e:
        # Captura exceções que ocorrerem dentro do bloco try.
        # Exception é a classe-base da maioria dos erros comuns
        # que podem ser capturados dessa forma.
        #
        # A variável e recebe o objeto da exceção, que contém
        # informações sobre o erro ocorrido.

        print(f"Erro durante a execução: {e}")
        # Exibe a mensagem da exceção no terminal.
        # Isso ajuda a identificar problemas na execução.

        sys.exit(1)
        # Encerra o programa com código de saída 1,
        # indicando que ocorreu um erro.


# =============================================================
# 6. PONTO DE ENTRADA DO PROGRAMA
# =============================================================

if __name__ == "__main__":
    # Verifica se este arquivo está sendo executado diretamente.
    #
    # Quando executamos o arquivo com um comando como:
    # python radar.py
    #
    # A variável especial __name__ recebe o valor "__main__".
    #
    # Se o arquivo for importado por outro módulo Python,
    # normalmente __name__ receberá o nome do módulo,
    # e o bloco abaixo não será executado automaticamente.

    main()
    # Chama a função principal.
    # A partir daqui, o programa inicia seu fluxo:
    #
    # 1. Pesquisa oportunidades usando o Gemini.
    # 2. Recebe o texto gerado.
    # 3. Verifica se existe conteúdo.
    # 4. Divide o texto em blocos.
    # 5. Envia as mensagens ao Telegram.
    # 6. Exibe mensagens de acompanhamento no terminal.
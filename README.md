# Cidadão Fácil — Burocracia Zero

Plataforma web desenvolvida em Python para facilitar o acesso a informações sobre serviços públicos brasileiros. O sistema reúne guias práticos, um catálogo de serviços, um simulador de documentos e um assistente com inteligência artificial integrado à **API do Groq**.

**Global Solution 2026.2 — FIAP | Ciência da Computação | 1º ano**  
**Case:** Citizen Assist AI

## Objetivo do Projeto

O Cidadão Fácil foi desenvolvido para:

- facilitar a busca por informações sobre serviços e documentos;
- explicar procedimentos em linguagem clara e acessível;
- orientar o cidadão por meio de perguntas em linguagem natural;
- apresentar referências de órgãos públicos para conferência;
- permitir acompanhar etapas de serviços e preparar uma solicitação;
- oferecer recursos básicos de acessibilidade;
- avaliar o uso do sistema com indicadores de atendimento.

## Funcionalidades

### Página inicial

Apresentação da plataforma, acesso rápido ao assistente, ao simulador e aos serviços em destaque.

### Catálogo de serviços

Pesquisa por palavras-chave, filtros por categoria e acesso a orientações relacionadas a CPF, Carteira de Identidade Nacional, Carteira de Trabalho Digital, título de eleitor, Cadastro Único, Meu SUS Digital e conta gov.br.

### Assistente com inteligência artificial

- Responde a perguntas com apoio de um modelo hospedado no Groq.
- Considera o histórico recente da conversa para entender perguntas de acompanhamento.
- Utiliza informações de serviços cadastrados em JSON.
- Mostra links oficiais relacionados ao assunto.
- Permite copiar, ouvir e avaliar a utilidade de respostas.
- Oferece entrada por voz em navegadores compatíveis.

### Guias interativos

Passos organizados por serviço, com checklist de acompanhamento. As marcações são guardadas no próprio navegador.

### Simulador de documentos

Um questionário de três etapas identifica o serviço, a situação do cidadão e a preferência por atendimento digital ou presencial. Ao final, apresenta orientações e pontos a conferir nos canais oficiais.

### Painel de indicadores

Mostra quantidade de consultas concluídas, tempo médio de resposta, avaliações de utilidade e desempenho da classificação local de assuntos. **A taxa de classificação não representa a taxa de acerto factual das respostas da IA.**

### Transparência e acessibilidade

Página de fontes e limitações, ajuste do tamanho da letra, alto contraste, navegação responsiva e avisos sobre privacidade.

## Tecnologias Utilizadas

- Python 3.10 ou superior
- Groq API e SDK oficial `groq`
- HTML5, CSS3 e JavaScript
- JSON para a base de serviços
- CSV para registro de indicadores
- Servidor HTTP da biblioteca padrão do Python
- Git e GitHub para versionamento
- PyCharm para desenvolvimento e execução

## Estrutura do Projeto

```text
Cidadao-Facil-GS2026/
├── main.py
├── avaliar.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   ├── servicos.json
│   └── avaliacao_perguntas.json
├── src/
│   ├── __init__.py
│   ├── ia.py
│   ├── servicos.py
│   ├── simulador.py
│   ├── seguranca.py
│   ├── indicadores.py
│   └── metricas.py
├── templates/
│   └── index.html
├── static/
│   ├── app.js
│   └── style.css
├── output/
├── tests/
│   ├── test_core.py
│   ├── test_conversa.py
│   ├── test_funcionalidades.py
│   └── test_server.py
└── docs/
    ├── FONTES_E_LIMITACOES.md
    ├── TESTES_USUARIOS.md
    └── PITCH_3_MINUTOS.md
```

O arquivo `.env` contém as configurações locais da API. Ele deve ser criado a partir de `.env.example` depois de clonar o repositório. No ZIP fornecido com o projeto, há também um `.env` já criado, com a chave em branco.

## Como Rodar o Projeto no PyCharm (do Zero)

### 1. Instalar Python, PyCharm e Git

Instale os programas abaixo:

- **Python:** https://www.python.org/downloads/
- **PyCharm:** https://www.jetbrains.com/pycharm/download/
- **Git:** https://git-scm.com/downloads

No Windows, selecione **Add Python to PATH** durante a instalação do Python, se a opção estiver disponível. No terminal, é possível verificar as instalações com:

```powershell
python --version
git --version
```

### 2. Clonar o repositório diretamente no PyCharm

1. Abra o **PyCharm**.
2. Na tela inicial, clique em **Clone Repository** (ou **Clone**).
3. Se o projeto já estiver aberto, use **Git > Clone** ou **VCS > Get from Version Control**.
4. Abra o repositório do projeto no GitHub, clique em **Code > HTTPS** e copie seu endereço.
5. Cole a URL no campo **URL** do PyCharm.
6. Escolha a pasta onde o projeto será salvo e clique em **Clone**.
7. Abra o projeto clonado e confirme que `main.py`, `requirements.txt` e `.env.example` aparecem na raiz.

**Alternativa:** se recebeu o projeto em ZIP, extraia o conteúdo e escolha **Open** na tela inicial do PyCharm. Selecione a pasta que contém `main.py`. Não é necessário clonar nesse caso.

### 3. Configurar o interpretador Python

O PyCharm pode sugerir a criação de um ambiente virtual para o projeto. Aceite a sugestão e selecione uma instalação do Python 3.10 ou superior.

Se precisar configurar manualmente:

1. Abra **File > Settings > Project > Python Interpreter** (a organização do menu pode variar).
2. Selecione um interpretador Python ou crie um ambiente virtual para o projeto.
3. Confirme que ele aparece como interpretador ativo.

O ambiente virtual do PyCharm é uma forma de isolar as bibliotecas do projeto. Não é necessário ativá-lo manualmente se o terminal e a execução já utilizam esse interpretador.

### 4. Instalar todas as dependências do requirements.txt

**Este passo é obrigatório antes de executar o site.**

1. No PyCharm, abra a aba **Terminal**, na parte inferior da janela.
2. Confirme que o terminal está na pasta que contém `main.py` e `requirements.txt`.
3. Execute:

```powershell
python -m pip install -r requirements.txt
```

Esse comando instala a biblioteca `groq` e suas dependências no Python usado pelo terminal.

Se o PyCharm exibir a opção **Install requirements** ao abrir `requirements.txt`, também é possível instalá-las por esse botão. Confira se a instalação foi realizada no mesmo interpretador selecionado no projeto.

### 5. Configurar a API do Groq

O assistente utiliza um modelo hospedado no Groq. Não é necessário instalar um modelo de IA no computador.

1. Entre em https://console.groq.com/ e acesse sua conta.
2. Na área de chaves de API, gere uma chave ou utilize uma chave Groq válida.
3. Na raiz do projeto, copie o arquivo `.env.example` e renomeie a cópia para `.env`.
4. Se estiver usando o ZIP que já contém `.env`, apenas abra esse arquivo.
5. Preencha a variável `GROQ_API_KEY`:

```env
AI_PROVIDER=groq
GROQ_API_KEY=COLE_SUA_CHAVE_AQUI
GROQ_MODEL=qwen/qwen3.8-27b
PORT=8000
ABRIR_NAVEGADOR=1
```

Salve o arquivo. O `.env` é usado localmente e está incluído no `.gitignore` para impedir a publicação de credenciais no GitHub.

### 6. Executar o projeto no PyCharm

Com as dependências instaladas e a API configurada:

1. Na árvore de arquivos, abra `main.py`.
2. Clique com o botão direito no arquivo e selecione **Run 'main'** (Executar `main`).
3. Aguarde a mensagem com o endereço do site.
4. O navegador deverá abrir automaticamente em:

**http://127.0.0.1:8000**

Se preferir iniciar pelo terminal integrado do PyCharm:

```powershell
python main.py
```

Para encerrar o servidor, pressione **Stop** no PyCharm ou `Ctrl+C` no terminal.

### 7. Verificar a conexão (opcional)

Se o assistente não estiver respondendo, abra o terminal do PyCharm e execute:

```powershell
python main.py --verificar
python main.py --diagnosticar
```

O primeiro comando verifica as configurações locais. O segundo testa uma conexão real com o Groq e informa possíveis problemas de acesso, modelo ou limite de requisições.

## Como Funciona o Sistema

Ao executar `main.py`, o programa:

1. Inicia o servidor local e disponibiliza as páginas web.
2. Carrega a base `data/servicos.json`.
3. Recebe perguntas e verifica se a entrada é válida.
4. Identifica os assuntos disponíveis com busca baseada em regras.
5. Envia a pergunta, o histórico recente e os trechos correspondentes à API do Groq.
6. Apresenta a resposta gerada e as referências cadastradas.
7. Registra indicadores anônimos de funcionamento e de feedback.

O catálogo, os guias e o simulador utilizam a base local de informações e podem ser consultados sem fazer chamadas à IA. O chat depende de uma chave Groq válida e de conexão com a internet.

## Base de Dados e Arquivos Principais

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Inicializa o servidor e disponibiliza as rotas do sistema |
| `src/ia.py` | Configura o Groq, constrói o contexto e solicita respostas ao modelo |
| `src/servicos.py` | Carrega e identifica serviços da base de conhecimento |
| `src/simulador.py` | Produz orientações conforme o questionário do simulador |
| `src/seguranca.py` | Valida as perguntas e bloqueia alguns padrões de dados pessoais |
| `src/metricas.py` | Registra eventos de uso e tempos de atendimento |
| `src/indicadores.py` | Calcula estatísticas e resultados da classificação |
| `data/servicos.json` | Cadastro de serviços, orientações e fontes oficiais |
| `data/avaliacao_perguntas.json` | Perguntas de referência para avaliação local |
| `static/style.css` | Layout responsivo e aparência das páginas |
| `static/app.js` | Navegação, chat, reconhecimento de voz, guias e gráficos |
| `output/metricas.csv` | Arquivo de indicadores criado ou atualizado com o uso |

## Testes e Indicadores

Para verificar o funcionamento das partes locais, execute no terminal do PyCharm:

```powershell
python -m unittest discover -s tests -v
```

Para avaliar a classificação de assuntos cadastrados:

```powershell
python avaliar.py
```

Os indicadores exibidos na interface refletem registros efetivos de uso. Consultas realizadas, duração e avaliações de utilidade **não comprovam** que todas as respostas da IA estão corretas. A avaliação de precisão exige comparação com fontes confiáveis e validação específica.

O arquivo `docs/TESTES_USUARIOS.md` contém orientações para registrar testes com usuários.

## Resolução de Problemas

| Situação | Solução |
|---|---|
| `main.py` ou `requirements.txt` não encontrado | Abra a pasta correta no PyCharm, onde estão esses dois arquivos |
| `No module named groq` | Instale `requirements.txt` usando o mesmo interpretador configurado no projeto |
| O chat informa que a IA está indisponível | Confirme `GROQ_API_KEY` no `.env` e reinicie o servidor |
| HTTP 403 ou modelo indisponível | Execute `python main.py --diagnosticar` e confira a permissão do modelo no Groq |
| A página não abre | Confira a porta indicada no terminal e se o servidor está em execução |
| Porta 8000 ocupada | Encerre outro servidor ou altere `PORT=8001` no `.env` |
| Entrada por voz indisponível | Use um navegador com suporte a reconhecimento de fala ou digite a pergunta |

## Limitações e Fontes

O Cidadão Fácil é independente e não representa órgãos governamentais. Não emite documentos nem realiza agendamentos. As orientações partem de uma base local, com referências oficiais, que não é atualizada automaticamente. O conteúdo gerado por IA pode conter imprecisões.

O texto das perguntas válidas é transmitido à API do Groq para gerar respostas; por isso, o usuário não deve informar senhas ou dados pessoais. As métricas locais não armazenam o conteúdo das perguntas. Para detalhes, consulte `docs/FONTES_E_LIMITACOES.md`.

## Integrantes

- **Marcos Peterson Martins Pereira — RM 573857**
- **Guilherme Vinciguerra Carvalho — RM 571951**

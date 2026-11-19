# Fontes, decisões de implementação e limitações

O Cidadão Fácil é um **assistente de orientação independente**. Não é canal oficial do governo, não emite documentos e não agenda atendimentos.

## De onde vêm as informações?

Os dados de serviços ficam em `data/servicos.json`. Cada item registra nome, categoria, descrição, orientações, observações e referências externas. O arquivo inclui orientações ligadas a:

- Carteira de Identidade Nacional (Governo Digital)
- CPF (Receita Federal)
- Carteira de Trabalho Digital (gov.br)
- Serviços eleitorais (TSE)
- Cadastro Único (Ministério do Desenvolvimento e Assistência Social)
- Meu SUS Digital (Ministério da Saúde)
- Conta gov.br (Governo Federal)

**O conteúdo é local e não é atualizado automaticamente.** Informações podem mudar e os links precisam ser periodicamente revisados pela equipe. O usuário deve confirmar requisitos, taxas e prazos no órgão competente.

## Como a IA responde?

1. O backend valida a pergunta e tenta identificar um assunto na base local.
2. O texto da pergunta e os dados dos serviços correspondentes são enviados ao **Groq**, pelo SDK oficial do provedor.
3. A resposta do modelo é exibida com links oficiais **retirados da base**, não links produzidos pelo modelo.
4. Quando não há fontes para um assunto, o sistema sinaliza estar fora do escopo.

Essa arquitetura reduz, mas **não elimina**, erros factuais, alucinações ou problemas de compreensão. Não há busca na internet em tempo real.

## Limitações do simulador

O simulador faz perguntas sobre serviço, situação e preferência de atendimento e apresenta etapas e alertas derivados da base. **Não analisa documentos, não calcula elegibilidade, não faz agendamento e não fornece uma relação definitiva de exigências.** Quando os documentos variam, ele orienta a confirmar no canal oficial.

## Privacidade

- O site não requer conta ou dados identificáveis.
- O texto das perguntas é enviado a um serviço externo de IA para gerar a resposta. Evite inserir dados pessoais, médicos, financeiros ou senhas.
- O servidor bloqueia alguns padrões básicos (CPF, e-mail e telefone), mas não garante detecção completa de informações pessoais.
- `output/metricas.csv` registra apenas evento, ID de serviço, horário, duração e avaliação de utilidade. Não armazena textos das perguntas.
- A marcação de passos fica em `localStorage` no dispositivo, sem envio ao servidor.
- O ditado por voz, se usado, depende das permissões e dos serviços de reconhecimento do próprio navegador.

## Indicadores

A página `/indicadores` lê registros locais e calcula contagens e médias reais. Exibe também o desempenho da **classificação local de assuntos** no conjunto `data/avaliacao_perguntas.json`. Essa porcentagem **não mede a acurácia das respostas geradas pela IA**. Para medir essa qualidade, é preciso um protocolo separado com respostas oficiais de referência e validação humana.

## Escopo de demonstração

O servidor escuta em `127.0.0.1` e deve ser usado localmente. Não há autenticação de usuários, infraestrutura de produção, auditoria de acessibilidade completa nem ferramentas de atualização automática das fontes.


## Orientações de CPF e atendimento presencial

A base local incluiu informações de atendimento presencial por Receita Federal, PAV e unidades conveniadas (Banco do Brasil, Caixa, Correios e cartórios conveniados). Segundo o Portal gov.br, inscrição digital direta é gratuita e a rede conveniada pode cobrar até R$ 7,00. O cartão plástico de CPF não é mais emitido; existe comprovante imprimível.

Fontes oficiais adicionais:
- https://www.gov.br/receitafederal/pt-br/canais_atendimento/fale-conosco/presencial
- https://www.gov.br/pt-br/servicos/inscrever-no-cpf
- https://www.gov.br/pt-br/servicos/obter-cartao-de-cpf

A informação pode mudar. O sistema não verifica automaticamente horários, unidades, documentação nem agendamentos em tempo real.

# Roteiro de pitch — Cidadão Fácil (até 3 minutos)

**Global Solution 2026.2 — Citizen Assist AI**  
**Objetivo:** demonstrar um problema social real, solução, funcionalidades, uso da IA, responsabilidade e impacto.  
**Duração-alvo:** 2min45s–2min55s (cronometrar a gravação).

## 00:00–00:30 — O problema

> "Você já tentou tirar um documento ou acessar um serviço público e ficou perdido entre sites, nomes diferentes e exigências difíceis de entender? A informação existe, mas nem sempre é simples de encontrar. Isso afeta especialmente quem tem pouca familiaridade com tecnologia."

**Tela:** início do Cidadão Fácil, slogan e os três caminhos de acesso.

## 00:30–01:00 — A solução

> "Por isso criamos o Cidadão Fácil: uma plataforma independente e gratuita que reúne informações verificáveis e orienta o cidadão. Ela oferece catálogo de serviços, guias práticos, um simulador e um assistente de inteligência artificial, sem exigir cadastro ou dados pessoais."

**Tela:** abrir catálogo; filtrar por "CPF"; mostrar o resultado.

## 01:00–01:50 — Demonstração

> "Se a pessoa precisa emitir CPF, pode abrir o guia, acompanhar as etapas e marcar as que já realizou. Se não souber por onde começar, o simulador faz três perguntas simples e apresenta orientações iniciais e fontes para confirmação. E, se tiver dúvidas, pode perguntar à IA com suas próprias palavras, inclusive por voz em navegadores compatíveis."

**Tela:** guia de CPF → marcar etapa → simulador (mostrar resultado) → assistente perguntar "Como emitir CPF?" → abrir link oficial. Evitar mostrar `.env`, token ou dados de pessoas reais.

## 01:50–02:20 — Tecnologia e segurança

> "A aplicação foi desenvolvida com Python, HTML, CSS e JavaScript e utiliza a API Groq para gerar respostas a partir de uma base de serviços estruturada. Tratamos entradas inválidas, não guardamos perguntas no relatório de métricas e deixamos claro que a IA pode errar. Por isso, cada orientação tem referências oficiais."

**Tela:** mostrar indicador real de uso e seção Transparência. Não confundir taxa de identificação de assunto com precisão da IA.

## 02:20–02:50 — Impacto e conclusão

> "Queremos reduzir a dificuldade de acesso a serviços e tornar a tecnologia uma ponte, não uma barreira. O próximo passo é validar o protótipo com cidadãos reais, medindo tempo para achar informações, facilidade e correção das orientações. Cidadão Fácil: informação simples para todos."

**Tela:** voltar ao início e encerrar com o slogan.

## Antes da gravação

- [ ] Fechar qualquer servidor antigo e iniciar o projeto atualizado antes da gravação.
- [ ] Executar `python main.py --diagnosticar` para confirmar o acesso real ao Groq.
- [ ] Escolher apenas serviços já cadastrados, com links oficiais existentes.
- [ ] Não mostrar o arquivo `.env`, a chave, dados pessoais nem mensagens de erro contendo informações privadas.
- [ ] Deixar catálogo, guia e simulador preparados para a demonstração.
- [ ] Testar a voz somente no navegador que oferece suporte; é opcional mostrar esse recurso.
- [ ] Se apresentar estatísticas, usar apenas dados verdadeiros. Os testes com usuários ainda precisam ser realizados.
- [ ] Cronometrar e manter o vídeo final em **até 3 minutos**.

# Plano de testes com usuários — Cidadão Fácil 9.0

**Situação:** plano de validação. Nenhum teste humano foi executado automaticamente e **não há resultados preenchidos**.

## Participantes e privacidade

Convide voluntários que não participaram do desenvolvimento; três ou mais oferecem uma demonstração inicial, mas não constituem estudo estatístico representativo. Não solicite nome, CPF, documento, e-mail ou outras informações pessoais. Identifique cada participante apenas por P1, P2, P3 etc.

## Tarefas sugeridas

1. **Catálogo:** localizar o serviço CPF usando a busca e abrir o guia.
2. **Guias:** marcar duas etapas do guia como concluídas; explicar que a marcação não confirma a emissão do documento.
3. **Simulador:** selecionar CPF → primeira solicitação → internet e localizar uma fonte oficial.
4. **Assistente:** fazer a pergunta “Como emitir CPF?” e identificar o primeiro passo e o link para confirmar.
5. **Acessibilidade:** aumentar a fonte, ativar contraste e, se o navegador permitir, ditar uma pergunta por voz.
6. **Transparência:** encontrar o aviso de que o site não é oficial e não realiza agendamentos.

## Modelo para preencher com resultados reais

| ID anônimo | Tarefa | Concluiu? | Orientação correta conforme fonte oficial? | Tempo (s) | Facilidade (1–5) | Observação sem dados pessoais |
|---|---|---|---|---|---|---|
| P1 | Catálogo | — | — | — | — | — |
| P1 | Guia | — | — | — | — | — |
| P1 | Simulador | — | — | — | — | — |
| P1 | Assistente | — | — | — | — | — |
| P2 | Catálogo | — | — | — | — | — |
| P2 | Guia | — | — | — | — | — |
| P2 | Simulador | — | — | — | — | — |
| P2 | Assistente | — | — | — | — | — |
| P3 | Catálogo | — | — | — | — | — |
| P3 | Guia | — | — | — | — | — |
| P3 | Simulador | — | — | — | — | — |
| P3 | Assistente | — | — | — | — | — |

## Indicadores recomendados

- **Taxa de conclusão de tarefas** = tarefas concluídas / tarefas propostas × 100.
- **Acerto de orientações** = orientações corretas conforme revisão humana de fontes oficiais / orientações avaliadas × 100.
- **Tempo médio para encontrar informação** = soma dos tempos humanos / quantidade de tarefas concluídas.
- **Facilidade média** = soma das notas / total de respostas válidas.
- **Avaliação qualitativa** = registrar barreiras de navegação sem coletar dados pessoais.

**Não confundir:** `/indicadores` exibe tempo de processamento do servidor/Groq e feedback voluntário. `python avaliar.py` avalia a **classificação do assunto** em perguntas rotuladas. Nenhum dos dois substitui os indicadores de teste humano acima.

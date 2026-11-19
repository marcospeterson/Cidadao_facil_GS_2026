"""Avalia identificação de serviços. NÃO mede a qualidade factual de respostas geradas pela IA."""
import json
from pathlib import Path
from src.servicos import carregar_servicos, localizar_servicos

raiz = Path(__file__).resolve().parent
casos = json.loads((raiz / 'data' / 'avaliacao_perguntas.json').read_text(encoding='utf-8'))
servicos = carregar_servicos()
acertos = 0
for n, item in enumerate(casos, 1):
    resultados = localizar_servicos(item['pergunta'], servicos)
    previsto = resultados[0]['id'] if resultados else None
    certo = previsto == item['servico_esperado']
    acertos += certo
    print(f"{n:02d}. {'OK' if certo else 'FALHOU'} | previsto: {previsto or 'fora de escopo'} | esperado: {item['servico_esperado'] or 'fora de escopo'} | {item['pergunta']}")
print(f"\nAcurácia da CLASSIFICAÇÃO DE ASSUNTO: {acertos}/{len(casos)} = {acertos/len(casos)*100:.1f}%")
print('ATENÇÃO: não é a acurácia factual das respostas da IA nem substitui testes com usuários.')

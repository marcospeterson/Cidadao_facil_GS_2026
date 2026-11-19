"""Indicadores anônimos de uso; métricas de teste ≠ taxa de acerto da IA."""
from __future__ import annotations

import csv
from collections import Counter
from src import metricas
from src.servicos import localizar_servicos


def relatorio(catalogo: list[dict], perguntas_avaliacao: list[dict]) -> dict:
    with metricas.TRAVA:
        if metricas.DESTINO.exists():
            with metricas.DESTINO.open(encoding="utf-8", newline="") as arq:
                registros = list(csv.DictReader(arq))
        else:
            registros = []
    sucessos = [r for r in registros if r.get("evento") == "sucesso"]
    tempos = []
    for r in sucessos:
        try:
            n = int(r.get("tempo_ms", ""))
            if 0 <= n < 600000:
                tempos.append(n)
        except (TypeError, ValueError):
            continue
    avaliacoes = [r for r in registros if r.get("evento") == "avaliacao"]
    uteis = sum(r.get("avaliacao") == "util" for r in avaliacoes)
    contagem = Counter(r.get("servico") for r in sucessos)
    por_servico = [{"id": s["id"], "nome": s["nome"], "total": contagem.get(s["id"], 0)} for s in catalogo]
    eventos = Counter(r.get("evento", "") for r in registros)
    dias = Counter(r.get("data_utc", "")[:10] for r in sucessos if r.get("data_utc"))
    # Métrica da regra local de roteamento por perguntas já rotuladas; NÃO mede respostas da IA.
    total_testes, acertos = 0, 0
    for caso in perguntas_avaliacao:
        pergunta = caso.get("pergunta", "")
        esperado = caso.get("servico_esperado", "") or ""
        if not isinstance(pergunta, str) or not isinstance(esperado, str):
            continue
        total_testes += 1
        achados = localizar_servicos(pergunta, catalogo)
        if (achados[0]["id"] if achados else "") == esperado:
            acertos += 1
    return {
        "consultas_concluidas": len(sucessos),
        "tempo_medio_ms": round(sum(tempos) / len(tempos)) if tempos else None,
        "total_avaliacoes": len(avaliacoes),
        "avaliacoes_uteis": uteis,
        "avaliacoes_nao_uteis": len(avaliacoes) - uteis,
        "percentual_util": round(100 * uteis / len(avaliacoes), 1) if avaliacoes else None,
        "eventos": {k: eventos.get(k, 0) for k in ("sucesso", "erro_api", "sem_api", "fora_escopo", "entrada_invalida", "simulador")},
        "por_servico": por_servico,
        "por_dia": [{"data": k, "total": v} for k, v in sorted(dias.items())[-7:]],
        "avaliacao_regras": {"total": total_testes, "acertos": acertos,
                              "percentual": round(100 * acertos / total_testes, 1) if total_testes else None,
                              "descricao": "Testes locais de identificação de assunto; não medem a precisão factual da IA."},
        "fonte": "output/metricas.csv (sem guardar perguntas ou dados pessoais)",
    }

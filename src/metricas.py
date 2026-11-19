"""Indicadores técnicos anônimos: nenhum conteúdo de pergunta é armazenado."""
from __future__ import annotations
import csv
import threading
from datetime import datetime, timezone
from pathlib import Path

DESTINO = Path(__file__).resolve().parent.parent / "output" / "metricas.csv"
CAMPOS = ["data_utc", "evento", "servico", "tempo_ms", "avaliacao"]
TRAVA = threading.Lock()
EVENTOS = {"sucesso", "sem_api", "erro_api", "fora_escopo", "entrada_invalida", "avaliacao", "simulador"}


def registrar(evento: str, servico: str = "", tempo_ms: int = 0, avaliacao: str = "") -> None:
    if evento not in EVENTOS:
        return
    with TRAVA:
        DESTINO.parent.mkdir(parents=True, exist_ok=True)
        novo = not DESTINO.exists()
        with DESTINO.open("a", encoding="utf-8", newline="") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=CAMPOS)
            if novo:
                writer.writeheader()
            writer.writerow({"data_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                             "evento": evento, "servico": servico if servico.isalnum() else "",
                             "tempo_ms": round(max(0, tempo_ms)),
                             "avaliacao": avaliacao if avaliacao in ("util", "nao_util") else ""})


def resumo() -> dict:
    if not DESTINO.exists():
        return {"consultas_concluidas": 0, "tempo_medio_ms": None, "avaliacoes_uteis": 0, "total_avaliacoes": 0}
    with TRAVA:
        with DESTINO.open(encoding="utf-8", newline="") as arquivo:
            linhas = list(csv.DictReader(arquivo))
    sucessos = [r for r in linhas if r.get("evento") == "sucesso"]
    tempos = [int(r["tempo_ms"]) for r in sucessos if r.get("tempo_ms", "").isdigit()]
    avaliacoes = [r for r in linhas if r.get("evento") == "avaliacao"]
    return {
        "consultas_concluidas": len(sucessos),
        "tempo_medio_ms": round(sum(tempos) / len(tempos)) if tempos else None,
        "avaliacoes_uteis": sum(r.get("avaliacao") == "util" for r in avaliacoes),
        "total_avaliacoes": len(avaliacoes),
    }

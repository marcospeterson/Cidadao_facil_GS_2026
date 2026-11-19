"""Base e identificação de serviços públicos via regras verificáveis."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent.parent / "data" / "servicos.json"
STOPWORDS = {
    "a", "as", "o", "os", "de", "do", "da", "dos", "das", "um", "uma", "me", "meu", "minha", "minhas", "meus",
    "para", "por", "com", "como", "qual", "que", "quero", "preciso", "ter", "fazer", "tirar", "obter", "solicitar",
    "onde", "no", "na", "nos", "nas", "eu", "e", "em", "se", "vou", "posso", "ajuda", "ajudar", "sobre"
}


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", texto)).strip()


def carregar_servicos() -> list[dict]:
    with ARQUIVO.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def tokens(texto: str) -> set[str]:
    return {w for w in normalizar(texto).split() if w not in STOPWORDS and len(w) >= 2}


def localizar_servicos(pergunta: str, catalogo: list[dict] | None = None, limite: int = 2) -> list[dict]:
    if catalogo is None:
        catalogo = carregar_servicos()
    q = normalizar(pergunta)
    qt = tokens(pergunta)
    candidatos = []
    for servico in catalogo:
        pontuacao = 0.0
        for termo in servico["atalhos"]:
            alias = normalizar(termo)
            at = tokens(termo)
            # Frases completas e siglas dão mais precisão que palavras soltas.
            if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", q):
                pontuacao += 5 + min(len(at), 3)
            elif at and len(at) > 1 and at.issubset(qt):
                pontuacao += 2
            elif len(at) == 1 and next(iter(at)) in qt:
                pontuacao += 2
        pontuacao += len(qt & tokens(servico["nome"])) * 0.8
        if pontuacao >= 2:
            candidatos.append((pontuacao, servico))
    candidatos.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in candidatos[:limite]]


def servico_por_id(identificador: str, catalogo: list[dict] | None = None) -> dict | None:
    if catalogo is None:
        catalogo = carregar_servicos()
    return next((s for s in catalogo if s["id"] == identificador), None)


def parece_continuacao(pergunta: str) -> bool:
    """Permite perguntas curtas relacionadas a um assunto já selecionado."""
    q = normalizar(pergunta)
    if len(q.split()) > 17:
        return False
    # Perguntas longas sem referência ao assunto anterior não devem herdar contexto.
    # Ex.: "Quanto custa um notebook gamer ..." não continua uma conversa sobre CPF.
    if len(q.split()) > 8 and not q.startswith(("e ", "se nao ", "nesse caso", "e quando ")):
        return False
    inicios = ("e ", "qual ", "quais ", "quanto ", "quantos ", "onde ", "precisa ",
               "tem ", "demora ", "posso ", "nesse caso", "e se ", "depois ",
               "mais detalhes", "como assim", "isso ", "quais sao ", "o que ",
               "se nao ", "e quando ", "em qual ", "em que ", "qual agencia ",
               "e no ", "e na ", "tem algum ", "me explica ", "e pra ")
    return q.startswith(inicios)

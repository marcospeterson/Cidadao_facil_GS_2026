"""Proteções básicas: dados sensíveis, injeção no conteúdo e limites de entrada."""
import re

# Não registramos e não enviamos perguntas que já contenham esses padrões à API externa.
PADROES_SENSIVEIS = [
    re.compile(r"(?<!\d)(?:\d{3}[.\s-]?\d{3}[.\s-]?\d{3}[-.\s]?\d{2})(?!\d)"),  # CPF
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),  # e-mail
    re.compile(r"(?<!\d)(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?9\d{4}[-\s]?\d{4}(?!\d)"),  # celular
]


def contem_dados_pessoais(texto: str) -> bool:
    return any(p.search(texto) for p in PADROES_SENSIVEIS)


def validar_pergunta(texto: object) -> str | None:
    if not isinstance(texto, str):
        return "Escreva uma pergunta em texto."
    texto = texto.strip()
    if len(texto) < 4:
        return "Escreva uma pergunta um pouco mais detalhada."
    if len(texto) > 800:
        return "Sua pergunta ficou muito longa. Use até 800 caracteres."
    if contem_dados_pessoais(texto):
        return "Por segurança, não envie CPF, número de celular ou e-mail aqui. Remova esses dados e tente novamente."
    return None

"""Simulador educativo de orientações: sem CPF, cadastro ou elegibilidade automática.

Não afirma que uma lista seja completa. Reutiliza apenas os dados locais curados.
"""
from __future__ import annotations

from src.servicos import servico_por_id

SITUACOES = {
    "primeira_vez": "Primeira solicitação / primeiro acesso",
    "segunda_via": "Segunda via ou recuperação de acesso",
    "atualizacao": "Atualização ou regularização",
    "consulta": "Apenas consultar informações",
}
MODALIDADES = {"digital": "Prefiro começar pela internet", "presencial": "Prefiro atendimento presencial", "indefinida": "Ainda não sei"}

# Indicações conservadoras, específicas por tema e baseadas no catálogo local.
# As regras variam conforme órgão, estado e situação; nunca tratá-las como checklist exaustivo.
OBSERVACOES_DOCUMENTOS = {
    "cin": ["Certidão de nascimento ou casamento costuma ser exigida na emissão da CIN.",
            "Confira no instituto de identificação do seu estado se há exigências adicionais."],
    "cpf": ["Os documentos podem variar conforme a idade e a situação cadastral.",
            "Confira os requisitos específicos do serviço escolhido na Receita Federal."],
    "trabalho": ["O acesso digital utiliza a conta gov.br; faça login somente no portal oficial.",
                "Confirme eventuais documentos para correções diretamente com o órgão responsável."],
    "eleitoral": ["Os documentos exigidos variam conforme a operação eleitoral solicitada.",
                  "Consulte requisitos e prazos no Autoatendimento Eleitoral do TSE."],
    "cadunico": ["O município informa os documentos para o cadastro e atualização familiar.",
                "Consulte o CRAS ou posto municipal antes de comparecer."],
    "sus": ["O acesso digital ocorre nos canais oficiais do Meu SUS Digital.",
            "Se houver divergência de dados, procure o suporte oficial ou a unidade de saúde."],
    "govbr": ["A conta deve ser criada ou recuperada somente nos canais oficiais do gov.br.",
              "Nunca forneça senhas ou códigos de segurança ao Cidadão Fácil."],
}


def simular(catalogo: list[dict], servico_id: str, situacao: str, modalidade: str) -> dict:
    if not all(isinstance(x, str) for x in (servico_id, situacao, modalidade)):
        raise ValueError("Escolha um serviço, uma situação e uma preferência de atendimento.")
    servico = servico_por_id(servico_id, catalogo)
    if servico is None:
        raise ValueError("Serviço não encontrado no catálogo.")
    if situacao not in SITUACOES:
        raise ValueError("Selecione uma situação válida.")
    if modalidade not in MODALIDADES:
        raise ValueError("Selecione uma preferência de atendimento válida.")
    complemento = {
        "digital": "Confira se o serviço selecionado oferece solicitação digital na fonte oficial.",
        "presencial": "Antes de se deslocar, confirme o endereço, documentos e se é necessário agendar.",
        "indefinida": "Consulte o órgão responsável para descobrir as opções de atendimento disponíveis.",
    }[modalidade]
    return {
        "servico": servico["id"],
        "nome": servico["nome"],
        "situacao": SITUACOES[situacao],
        "modalidade": MODALIDADES[modalidade],
        "etapas": list(servico["orientacoes"]) + [complemento],
        "documentos": OBSERVACOES_DOCUMENTOS[servico["id"]],
        "observacoes": servico["observacoes"],
        "fontes": servico["fontes"],
        "aviso": "Simulação educativa, não oficial. Não verifica documentos pessoais, elegibilidade ou disponibilidade. "
                 "As exigências podem variar; confirme nos links oficiais antes de solicitar o serviço.",
    }

"""Cidadão Fácil — Global Solution 2026.2. Iniciar: python main.py"""
from __future__ import annotations

import json
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Timer
from urllib.parse import unquote, urlsplit

from src.ia import (ARQUIVO_ENV, ErroIA, chave_configurada, configuracao,
                    responder, testar_conexao, testar_autenticacao, valor_env)
from src.indicadores import relatorio
from src.metricas import registrar, resumo
from src.seguranca import validar_pergunta
from src.servicos import carregar_servicos, localizar_servicos, parece_continuacao, servico_por_id
from src.simulador import simular, SITUACOES, MODALIDADES

RAIZ = Path(__file__).resolve().parent
VERSAO = "9.0"
CATALOGO = carregar_servicos()
with (RAIZ / "data" / "avaliacao_perguntas.json").open(encoding="utf-8") as _arq:
    PERGUNTAS_AVALIACAO = json.load(_arq)

PAGINAS = {"/", "/servicos", "/assistente", "/guias", "/simulador", "/indicadores", "/transparencia"}
ARQUIVOS = {
    **{p: ("templates/index.html", "text/html; charset=utf-8") for p in PAGINAS},
    "/static/style.css": ("static/style.css", "text/css; charset=utf-8"),
    "/static/app.js": ("static/app.js", "text/javascript; charset=utf-8"),
}


def publico(servico: dict, completo: bool = False) -> dict:
    campos = ("id", "nome", "categoria", "descricao", "fontes", "orientacoes", "observacoes") if completo else (
        "id", "nome", "categoria", "descricao", "fontes")
    return {k: servico[k] for k in campos}


class Atendimento(BaseHTTPRequestHandler):
    def _cabecalhos(self, tipo: str, tamanho: int) -> None:
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(tamanho))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")

    def _json(self, codigo: int, payload: dict | list) -> None:
        dados = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self._cabecalhos("application/json; charset=utf-8", len(dados))
        self.end_headers()
        self.wfile.write(dados)

    def _receber_json(self) -> dict | None:
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
        except (TypeError, ValueError):
            return None
        if not 0 < tamanho <= 8192:
            return None
        try:
            carga = json.loads(self.rfile.read(tamanho))
        except (json.JSONDecodeError, UnicodeError):
            return None
        return carga if isinstance(carga, dict) else None

    def do_GET(self) -> None:
        caminho = unquote(urlsplit(self.path).path).rstrip("/") or "/"
        if caminho == "/api/servicos":
            self._json(200, [publico(s) for s in CATALOGO])
            return
        if caminho.startswith("/api/servicos/"):
            ident = caminho.rsplit("/", 1)[-1]
            s = servico_por_id(ident, CATALOGO)
            self._json(200, publico(s, completo=True)) if s else self._json(404, {"erro": "Serviço não encontrado."})
            return
        if caminho == "/api/simulador/opcoes":
            self._json(200, {"situacoes": SITUACOES, "modalidades": MODALIDADES})
            return
        if caminho == "/api/status":
            try:
                cfg = configuracao()
                self._json(200, {"configurado": chave_configurada(cfg["chave"]), "provedor": "groq",
                                 "modelo": cfg["modelo"], "env_presente": cfg["arquivo_existe"], "versao": VERSAO})
            except ErroIA as erro:
                self._json(200, {"configurado": False, "provedor": "groq", "erro": str(erro), "versao": VERSAO})
            return
        if caminho == "/api/metricas":
            self._json(200, resumo())  # Compatibilidade com a versão anterior.
            return
        if caminho == "/api/indicadores":
            self._json(200, relatorio(CATALOGO, PERGUNTAS_AVALIACAO))
            return
        recurso = ARQUIVOS.get(caminho)
        if recurso is None:
            self._json(404, {"erro": "Página não encontrada."})
            return
        arquivo = RAIZ / recurso[0]
        if not arquivo.is_file():
            self._json(500, {"erro": "Arquivo da interface ausente."})
            return
        dados = arquivo.read_bytes()
        self.send_response(200)
        self._cabecalhos(recurso[1], len(dados))
        self.end_headers()
        self.wfile.write(dados)

    def do_POST(self) -> None:
        caminho = urlsplit(self.path).path
        inicio = time.perf_counter()
        payload = self._receber_json()
        if payload is None:
            self._json(400, {"erro": "Envie um JSON válido (até 8 KB)."})
            return
        if caminho == "/api/feedback":
            avaliacao = payload.get("avaliacao")
            if avaliacao not in ("util", "nao_util"):
                self._json(400, {"erro": "Avaliação inválida."})
                return
            registrar("avaliacao", avaliacao=avaliacao)
            self._json(200, {"ok": True})
            return
        if caminho == "/api/simular":
            try:
                dados = simular(CATALOGO, payload.get("servico"), payload.get("situacao"), payload.get("modalidade"))
            except ValueError as erro:
                self._json(400, {"erro": str(erro)})
                return
            registrar("simulador", servico=dados["servico"])
            self._json(200, dados)
            return
        if caminho != "/api/perguntar":
            self._json(404, {"erro": "Rota não encontrada."})
            return
        pergunta = payload.get("pergunta", "")
        erro = validar_pergunta(pergunta)
        if erro:
            registrar("entrada_invalida")
            self._json(400, {"erro": erro})
            return
        id_escolhido = payload.get("servico", "")
        escolhido = servico_por_id(id_escolhido, CATALOGO) if isinstance(id_escolhido, str) else None
        encontrados = [escolhido] if escolhido else localizar_servicos(pergunta, CATALOGO)
        if not encontrados and parece_continuacao(pergunta):
            contexto_id = payload.get("contexto_servico", "")
            contexto = servico_por_id(contexto_id, CATALOGO) if isinstance(contexto_id, str) else None
            if contexto:
                encontrados = [contexto]
        if not encontrados:
            registrar("fora_escopo", tempo_ms=int((time.perf_counter() - inicio) * 1000))
            self._json(200, {"resposta": "Ainda não tenho fontes verificadas para esse assunto. Veja o catálogo de serviços disponíveis.",
                             "fontes": [], "servico": "", "modo": "fora_escopo", "tempo_ms": 0})
            return
        selecionado = encontrados[0]["id"]
        fontes = [{"titulo": f["titulo"], "orgao": f["orgao"], "url": f["url"]} for s in encontrados for f in s["fontes"]]
        try:
            historico = payload.get("historico", [])
            if not isinstance(historico, list):
                historico = []
            texto, modelo = responder(pergunta, encontrados, historico)
        except ErroIA as erro:
            registrar("sem_api" if "não configurada" in str(erro) else "erro_api", servico=selecionado,
                      tempo_ms=int((time.perf_counter() - inicio) * 1000))
            self._json(erro.status, {"erro": str(erro), "fontes": fontes, "servico": selecionado,
                                     "http_groq": erro.http_groq, "codigo_api": erro.codigo_api})
            return
        except Exception:
            registrar("erro_api", servico=selecionado)
            self._json(502, {"erro": "Falha ao consultar a IA. Execute python main.py --diagnosticar e verifique o terminal.", "fontes": fontes})
            return
        tempo = int((time.perf_counter() - inicio) * 1000)
        registrar("sucesso", servico=selecionado, tempo_ms=tempo)
        self._json(200, {"resposta": texto, "fontes": fontes, "servico": selecionado,
                         "modo": "ia", "modelo": modelo, "tempo_ms": tempo})


def main() -> None:
    if "--diagnosticar" in sys.argv or "--testar-api" in sys.argv:
        print(f"\n=== DIAGNÓSTICO GROQ / CIDADÃO FÁCIL {VERSAO} ===")
        print("Arquivo de configuração:", ARQUIVO_ENV)
        try:
            cfg = configuracao()
            print("Provedor:", cfg["provedor"], "| Modelo:", cfg["modelo"])
            print("Chave encontrada:", "SIM" if chave_configurada(cfg["chave"]) else "NÃO")
            print("[1/2] Verificando autenticação em /models...")
            quantidade = testar_autenticacao()
            print(f"  OK: {quantidade} modelos no catálogo disponível.")
            print("[2/2] Verificando acesso e resposta do modelo...")
            modelo = testar_conexao()
            print(f"  OK: Groq respondeu com {modelo}.")
            print("DIAGNÓSTICO: CONEXÃO CONFIRMADA. A chave não foi exibida.")
        except ErroIA as erro:
            print("DIAGNÓSTICO: FALHA —", erro)
            sys.exit(1)
        return
    if "--verificar" in sys.argv or "--check" in sys.argv:
        print(f"\n=== VERIFICAÇÃO LOCAL CIDADÃO FÁCIL {VERSAO} ===")
        print("Pasta:", RAIZ, "\nArquivo .env:", ARQUIVO_ENV)
        try:
            cfg = configuracao()
            print("Arquivo existe:", "SIM" if cfg["arquivo_existe"] else "NÃO")
            print("Provedor: Groq | Modelo:", cfg["modelo"])
            print("GROQ_API_KEY:", "PREENCHIDA" if chave_configurada(cfg["chave"]) else "VAZIA")
        except ErroIA as erro:
            print("Configuração inválida:", erro)
        return
    try:
        import groq  # noqa: F401
    except ImportError:
        print("Biblioteca groq ausente. Instale com: python -m pip install -r requirements.txt")
        sys.exit(1)
    try:
        porta = int(valor_env("PORT", "8000"))
        if not 1024 <= porta <= 65535:
            raise ValueError()
    except ValueError:
        print("PORT inválida no .env; escolha entre 1024 e 65535.")
        sys.exit(1)
    try:
        servidor = ThreadingHTTPServer(("127.0.0.1", porta), Atendimento)
    except OSError:
        print(f"ERRO: porta {porta} ocupada. Encerre servidores antigos com Ctrl+C e tente novamente.")
        sys.exit(1)
    url = f"http://127.0.0.1:{porta}"
    print("\n" + "=" * 55)
    print("CIDADÃO FÁCIL · SERVIDOR LOCAL")
    print("=" * 55)
    print("Projeto:", RAIZ)
    print("Arquivo .env:", ARQUIVO_ENV)
    try:
        cfg = configuracao()
        print("Modelo:", cfg["modelo"], "| Chave:", "PREENCHIDA" if chave_configurada(cfg["chave"]) else "PENDENTE")
    except ErroIA as erro:
        print("Configuração:", erro)
    print("Site:", url)
    print("Diagnóstico: python main.py --diagnosticar")
    print("Encerrar: Ctrl+C\n")
    if valor_env("ABRIR_NAVEGADOR", "1") != "0":
        Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()

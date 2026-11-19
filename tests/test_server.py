"""Testes da interface HTTP local (a API Groq é simulada)."""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

from main import Atendimento
from http.server import ThreadingHTTPServer


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.arquivo = Path(self.pasta.name) / '.env'
        self.arquivo.write_text('AI_PROVIDER=groq\nGROQ_API_KEY=\n', encoding='utf-8')
        self.mock_arquivo = patch('src.ia.ARQUIVO_ENV', self.arquivo)
        self.mock_arquivo.start()
        self.addCleanup(self.mock_arquivo.stop)
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Atendimento)
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def solicitar(self, caminho, payload=None):
        if payload is None:
            request = urllib.request.Request(self.url + caminho)
        else:
            request = urllib.request.Request(
                self.url + caminho,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST',
            )
        try:
            with urllib.request.urlopen(request, timeout=3) as resposta:
                return resposta.status, json.load(resposta)
        except urllib.error.HTTPError as erro:
            return erro.code, json.load(erro)

    def test_status_mostra_groq_e_env_existe(self):
        codigo, dados = self.solicitar('/api/status')
        self.assertEqual(codigo, 200)
        self.assertEqual(dados['provedor'], 'groq')
        self.assertEqual(dados['versao'], '9.0')
        self.assertFalse(dados['configurado'])
        self.assertTrue(dados['env_presente'])

    def test_pergunta_sem_chave_aponta_para_groq(self):
        codigo, dados = self.solicitar('/api/perguntar', {'pergunta':'Como emitir CPF?'})
        self.assertEqual(codigo, 503)
        self.assertIn('GROQ_API_KEY', dados['erro'])
        self.assertNotIn('XAI_API_KEY', dados['erro'])

    @patch('src.ia._post_json')
    def test_pergunta_com_chave_recebe_resposta_simulada(self, chamada):
        self.arquivo.write_text('AI_PROVIDER=groq\nGROQ_API_KEY=gsk_chave_de_teste\n', encoding='utf-8')
        chamada.return_value = {'choices':[{'message':{'content':'Confira a Receita Federal.'}}]}
        codigo, dados = self.solicitar('/api/perguntar', {'pergunta':'Como emitir CPF?'})
        self.assertEqual(codigo, 200)
        self.assertEqual(dados['modo'], 'ia')
        self.assertIn('Receita Federal', dados['resposta'])
        self.assertTrue(dados['fontes'])
        chamada.assert_called_once()

    @patch('src.ia._post_json')
    def test_403_mostra_motivo_sem_expor_chave(self, chamada):
        from src.ia import ErroIA
        self.arquivo.write_text('AI_PROVIDER=groq\nGROQ_API_KEY=gsk_chave_de_teste\n', encoding='utf-8')
        chamada.side_effect = ErroIA(
            'Groq HTTP 403 (código Groq: model_permission_blocked_project): '
            'Modelo bloqueado pelo PROJETO. Motivo informado: modelo não permitido.',
            502, 'model_permission_blocked_project', 403,
        )
        codigo, dados = self.solicitar('/api/perguntar', {'pergunta':'Como emitir CPF?'})
        self.assertEqual(codigo, 502)  # O servidor local traduz a recusa do provedor.
        self.assertEqual(dados['http_groq'], 403)
        self.assertEqual(dados['codigo_api'], 'model_permission_blocked_project')
        self.assertIn('modelo não permitido', dados['erro'])
        self.assertNotIn('gsk_chave_de_teste', json.dumps(dados))


if __name__ == '__main__':
    unittest.main()

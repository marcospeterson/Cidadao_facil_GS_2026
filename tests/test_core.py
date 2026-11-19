"""Teste com: python -m unittest discover -s tests -v (sem usar cota Groq)."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.ia import ErroIA, carregar_env, chave_configurada, configuracao, responder, testar_conexao, testar_autenticacao, _post_json, _requisitar_json, _erro_sdk
from src.seguranca import contem_dados_pessoais, validar_pergunta
from src.servicos import carregar_servicos, localizar_servicos, normalizar, servico_por_id, parece_continuacao


class ServicosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogo = carregar_servicos()

    def test_base_tem_sete_servicos(self):
        self.assertEqual(len(self.catalogo), 7)

    def test_normalizacao(self):
        self.assertEqual(normalizar('TÍTULO de Eleitor!'), 'titulo de eleitor')

    def test_fontes_sao_oficiais(self):
        for servico in self.catalogo:
            for fonte in servico['fontes']:
                self.assertTrue(fonte['url'].startswith('https://'))
                self.assertTrue('gov.br' in fonte['url'] or 'tse.jus.br' in fonte['url'])

    def test_identificacao_por_assunto(self):
        casos = [
            ('Perdi meu RG. Como faço segunda via?', 'cin'),
            ('Como regularizar meu CPF?', 'cpf'),
            ('Quero minha carteira de trabalho digital', 'trabalho'),
            ('Como tirar título de eleitor?', 'eleitoral'),
            ('O que é o Cadastro Único?', 'cadunico'),
            ('Como acesso o Cartão SUS?', 'sus'),
            ('Esqueci minha senha gov br', 'govbr'),
            ('Como consultar o e-Título?', 'eleitoral'),
            ('Preciso saber do CRAS', 'cadunico'),
            ('Onde tiro a nova identidade?', 'cin'),
            ('Quero acompanhar contratos pela CTPS Digital', 'trabalho'),
            ('Consultar situação do CPF', 'cpf'),
        ]
        for pergunta, esperado in casos:
            with self.subTest(pergunta=pergunta):
                encontrados = localizar_servicos(pergunta, self.catalogo)
                self.assertTrue(encontrados)
                self.assertEqual(encontrados[0]['id'], esperado)

    def test_fora_escopo(self):
        self.assertEqual(localizar_servicos('Qual a temperatura de Marte?'), [])

    def test_servico_inexistente(self):
        self.assertIsNone(servico_por_id('x', self.catalogo))

    def test_continuacao(self):
        self.assertTrue(parece_continuacao('E quais documentos preciso?'))
        self.assertFalse(parece_continuacao('Quanto custa um notebook gamer com processador de última geração?'))


class SegurancaTests(unittest.TestCase):
    def test_cpf(self):
        self.assertTrue(contem_dados_pessoais('Meu CPF é 123.456.789-09'))

    def test_email(self):
        self.assertTrue(contem_dados_pessoais('Meu e-mail é teste@exemplo.com'))

    def test_celular(self):
        self.assertTrue(contem_dados_pessoais('Telefone (11) 91234-5678'))

    def test_pergunta_geral(self):
        self.assertIsNone(validar_pergunta('Como emitir CPF?'))

    def test_entrada_vazia(self):
        self.assertIsNotNone(validar_pergunta(' '))

    def test_texto_longo(self):
        self.assertIsNotNone(validar_pergunta('a' * 801))


class GroqTests(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.arquivo_env = Path(self.pasta.name) / '.env'
        self.patch_env = patch('src.ia.ARQUIVO_ENV', self.arquivo_env)
        self.patch_env.start()
        self.addCleanup(self.patch_env.stop)

    def gravar(self, texto):
        self.arquivo_env.write_text(texto, encoding='utf-8')

    def test_ler_arquivo_env_criado(self):
        self.gravar('AI_PROVIDER=groq\nGROQ_API_KEY=gsk_teste\n')
        self.assertEqual(carregar_env()['GROQ_API_KEY'], 'gsk_teste')

    @patch.dict(os.environ, {'AI_PROVIDER':'xai','XAI_API_KEY':'antigo','GROQ_API_KEY':'chave-antiga'})
    def test_env_da_pasta_tem_prioridade_sobre_windows(self):
        self.gravar('AI_PROVIDER=groq\nGROQ_API_KEY=gsk_nova\nGROQ_MODEL=qwen/qwen3.8-27b\n')
        cfg = configuracao()
        self.assertEqual(cfg['provedor'], 'groq')
        self.assertEqual(cfg['chave'], 'gsk_nova')
        self.assertEqual(cfg['endpoint'], 'https://api.groq.com/openai/v1/chat/completions')

    @patch.dict(os.environ, {'GROQ_API_KEY':'chave-antiga'})
    def test_chave_vazia_do_env_nao_pega_chave_antiga(self):
        self.gravar('AI_PROVIDER=groq\nGROQ_API_KEY=\n')
        self.assertFalse(chave_configurada(configuracao()['chave']))

    def test_chave_de_exemplo_nao_e_considerada_valida(self):
        self.assertFalse(chave_configurada('COLE_SUA_CHAVE_GROQ_AQUI'))
        self.assertFalse(chave_configurada(''))
        self.assertTrue(chave_configurada('gsk_teste_qualquer'))

    @patch('src.ia._post_json')
    def test_enviar_contexto_para_groq(self, post):
        self.gravar('AI_PROVIDER=groq\nGROQ_API_KEY=gsk_teste\n')
        post.return_value = {'choices':[{'message':{'content':'Consulte a fonte oficial.'}}]}
        texto, modelo = responder('Meu CPF', [carregar_servicos()[1]])
        self.assertIn('Consulte', texto)
        self.assertEqual(modelo, 'qwen/qwen3.8-27b')
        endpoint, chave, corpo = post.call_args.args
        self.assertTrue(endpoint.endswith('/chat/completions'))
        self.assertEqual(chave, 'gsk_teste')
        self.assertEqual(corpo['messages'][0]['role'], 'system')
        self.assertIn('CPF', corpo['messages'][-1]['content'])

    def test_sem_chave_nao_chama_api_nem_pede_xai(self):
        self.gravar('AI_PROVIDER=groq\nGROQ_API_KEY=\n')
        with patch('src.ia._post_json') as post:
            with self.assertRaisesRegex(ErroIA, 'GROQ_API_KEY') as erro:
                responder('Meu CPF', [carregar_servicos()[1]])
            self.assertEqual(erro.exception.status, 503)
            post.assert_not_called()

    @patch('src.ia._post_json')
    def test_conexao_real_pode_ser_simulada(self, post):
        self.gravar('AI_PROVIDER=groq\nGROQ_API_KEY=gsk_teste\n')
        post.return_value = {"choices": [{"message": {"content": "OK"}}]}
        self.assertEqual(testar_conexao(), 'qwen/qwen3.8-27b')
        post.assert_called_once()
        corpo = post.call_args.args[2]
        self.assertNotIn('reasoning_effort', corpo)

    def test_modelo_padrao_atualizado(self):
        self.gravar('AI_PROVIDER=groq\nGROQ_API_KEY=gsk_teste\n')
        self.assertEqual(configuracao()['modelo'], 'qwen/qwen3.8-27b')

    def _erro_simulado(self, status, codigo='', mensagem=''):
        erro = Exception('groq api exception')
        erro.status_code = status
        erro.body = {'error': {'code': codigo, 'message': mensagem}}
        return erro

    def test_erro_401_explicito(self):
        with self.assertRaisesRegex(ErroIA, 'HTTP 401'):
            raise _erro_sdk(self._erro_simulado(401, 'invalid_api_key'), 'gsk_fake')

    def test_erro_modelo_descontinuado_explicito(self):
        erro = _erro_sdk(self._erro_simulado(403, 'model_decommissioned'), 'gsk_fake')
        self.assertIn('descontinuado', str(erro))

    def test_erro_403_bloqueio_de_projeto(self):
        erro = _erro_sdk(self._erro_simulado(403, 'model_permission_blocked_project', 'Model blocked'), 'gsk_fake')
        self.assertIn('PROJETO', str(erro))
        self.assertEqual(erro.http_groq, 403)
        self.assertEqual(erro.codigo_api, 'model_permission_blocked_project')

    def test_erro_403_bloqueio_organizacao(self):
        erro = _erro_sdk(self._erro_simulado(403, 'model_permission_blocked_org'), 'gsk_fake')
        self.assertIn('ORGANIZAÇÃO', str(erro))

    def test_403_retorna_mensagem_exata_sem_vazar_chave(self):
        erro = _erro_sdk(self._erro_simulado(403, 'permissions_error',
             'Access not allowed for this model on your project; key gsk_SECRETO_EXEMPLO'), 'gsk_SECRETO_EXEMPLO')
        self.assertIn('Access not allowed', str(erro))
        self.assertIn('permissions_error', str(erro))
        self.assertNotIn('gsk_SECRETO_EXEMPLO', str(erro))

    def test_403_cloudflare_1010_reconhecido(self):
        from types import SimpleNamespace
        erro = Exception('forbidden')
        erro.status_code = 403
        erro.body = None
        erro.response = SimpleNamespace(text='error code: 1010')
        erro.response.json = lambda: (_ for _ in ()).throw(ValueError())
        resultado = _erro_sdk(erro)
        self.assertIn('cloudflare_1010', str(resultado))

    @patch('src.ia._criar_cliente')
    def test_sdk_oficial_e_usado_para_chat(self, mock_cliente):
        from types import SimpleNamespace
        response = SimpleNamespace(model_dump=lambda: {'choices':[{'message':{'content':'OK'}}]})
        fake = mock_cliente.return_value
        fake.chat.completions.create.return_value = response
        resultado = _post_json('https://api.groq.com/openai/v1/chat/completions', 'gsk_fake',
              {'model':'qwen/qwen3.8-27b', 'messages':[{'role':'user','content':'Oi'}]})
        self.assertEqual(resultado['choices'][0]['message']['content'], 'OK')
        fake.chat.completions.create.assert_called_once()
        fake.close.assert_called_once()

    @patch('src.ia._criar_cliente')
    def test_sdk_oficial_e_usado_para_modelos(self, mock_cliente):
        from types import SimpleNamespace
        fake = mock_cliente.return_value
        fake.models.list.return_value = SimpleNamespace(model_dump=lambda: {'data':[{'id':'qwen'}]})
        resposta = _requisitar_json('https://api.groq.com/openai/v1/models', 'gsk_fake')
        self.assertEqual(len(resposta['data']), 1)
        fake.models.list.assert_called_once()

    @patch('src.ia._criar_cliente')
    def test_sdk_403_e_convertido_em_erro_seguro(self, mock_cliente):
        mock_cliente.return_value.chat.completions.create.side_effect = self._erro_simulado(403, 'model_permission_blocked_project', 'blocked')
        with self.assertRaises(ErroIA) as ctx:
            _post_json('https://api.groq.com/openai/v1/chat/completions', 'gsk_fake',
                       {'model':'qwen/qwen3.8-27b', 'messages':[]})
        self.assertEqual(ctx.exception.http_groq, 403)

    @patch('src.ia._post_json')
    def test_qwen_modo_direto(self, post):
        self.gravar('AI_PROVIDER=groq\nGROQ_API_KEY=gsk_teste\n')
        post.return_value = {'choices':[{'message':{'content':'Orientação.'}}]}
        texto, modelo = responder('Meu CPF', [carregar_servicos()[1]])
        self.assertEqual(modelo, 'qwen/qwen3.8-27b')
        self.assertNotIn('reasoning_effort', post.call_args.args[2])

    @patch('src.ia._requisitar_json')
    def test_autenticacao_nao_executa_modelo(self, requisitar):
        self.gravar('AI_PROVIDER=groq\nGROQ_API_KEY=gsk_teste\n')
        requisitar.return_value = {'data': [{'id': 'modelo1'}, {'id': 'modelo2'}]}
        self.assertEqual(testar_autenticacao(), 2)
        self.assertEqual(requisitar.call_args.args[1], 'gsk_teste')
        self.assertEqual(len(requisitar.call_args.args), 2)  # GET, sem corpo

    def test_provedor_antigo_gera_erro_orientativo(self):
        self.gravar('AI_PROVIDER=xai\nGROQ_API_KEY=gsk_teste\n')
        with self.assertRaisesRegex(ErroIA, 'AI_PROVIDER=groq'):
            configuracao()


if __name__ == '__main__':
    unittest.main()

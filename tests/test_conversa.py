"""Regressão: garantir que a IA receba foco na pergunta e fatos úteis."""
import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
from src.ia import responder, construir_contexto, prompt_sistema
from src.servicos import carregar_servicos, parece_continuacao


class ConversaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cpf = next(s for s in carregar_servicos() if s['id'] == 'cpf')

    def test_base_tem_fatos_de_atendimento_e_fontes(self):
        ctx = construir_contexto([self.cpf])
        for termo in ('Banco do Brasil', 'Correios', 'Caixa', 'R$ 7,00', 'cartórios', 'comprovante'):
            self.assertIn(termo, ctx)
        self.assertTrue(any('atendimento-presencial' in x['url'] or 'presencial' in x['url'] for x in self.cpf['fontes']))

    def test_prompt_diferencia_onde_de_como(self):
        texto = prompt_sistema()
        self.assertIn('ONDE ir', texto)
        self.assertIn('NÃO repita', texto)
        self.assertIn('pergunta MAIS RECENTE', texto)

    @patch('src.ia._post_json')
    def test_historico_e_nova_pergunta_sao_turnos_separados(self, post):
        post.return_value = {'choices': [{'message': {'content': 'Vá a um estabelecimento conveniado.'}}]}
        with TemporaryDirectory() as tmp:
            env = Path(tmp) / '.env'
            env.write_text('AI_PROVIDER=groq\nGROQ_API_KEY=gsk_teste\n', encoding='utf-8')
            with patch('src.ia.ARQUIVO_ENV', env):
                resposta, modelo = responder('Em que agência posso ir?', [self.cpf], [
                    {'role':'user', 'content':'Como emitir CPF?'},
                    {'role':'assistant', 'content':'Use a inscrição no site da Receita.'},
                ])
        self.assertIn('conveniado', resposta)
        messages = post.call_args.args[2]['messages']
        self.assertEqual([x['role'] for x in messages], ['system','user','assistant','user'])
        self.assertEqual(messages[-1]['content'], 'Em que agência posso ir?')
        self.assertNotIn('BASE DE SERVIÇOS', messages[-1]['content'])
        self.assertIn('Banco do Brasil', messages[0]['content'])
        self.assertNotIn('reasoning_effort', post.call_args.args[2])

    def test_continuacao_mais_longa(self):
        self.assertTrue(parece_continuacao('E se eu não conseguir fazer pela internet, onde posso ir pessoalmente?'))
        self.assertFalse(parece_continuacao('Quero saber o preço de um notebook gamer novo'))

if __name__ == '__main__': unittest.main()

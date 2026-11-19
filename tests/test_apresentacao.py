"""Verificações da apresentação pública e da documentação de instalação."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class FinalPresentationTests(unittest.TestCase):
    def test_no_release_copy_in_html_or_js(self):
        html = (ROOT / 'templates/index.html').read_text(encoding='utf-8')
        js = (ROOT / 'static/app.js').read_text(encoding='utf-8')
        self.assertNotIn('Versão 9.0', html)
        self.assertNotIn('Protótipo educacional', html)
        self.assertNotIn('Projeto acadêmico · GS', html)
        self.assertNotIn("'IA configurada · v'+status.versao", js)
        self.assertIn('Não é um canal oficial', html)

    def test_pycharm_instructions_and_members(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        for expected in ('PyCharm', 'Clone', 'requirements.txt', 'python main.py', 'GROQ_API_KEY',
                         'Marcos Peterson Martins Pereira — RM 573857', 'Guilherme Vinciguerra Carvalho — RM 571951'):
            self.assertIn(expected, readme)

if __name__ == '__main__':
    unittest.main()

"""Testes dos novos recursos, sem chamadas reais à API nem dados pessoais."""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer

from main import Atendimento, CATALOGO, PERGUNTAS_AVALIACAO
from src.indicadores import relatorio
from src.simulador import simular
from src.metricas import registrar


class FuncionalidadesTests(unittest.TestCase):
    def test_simulador_sete_servicos(self):
        for s in CATALOGO:
            with self.subTest(servico=s['id']):
                d=simular(CATALOGO,s['id'],'primeira_vez','indefinida')
                self.assertEqual(d['servico'],s['id'])
                self.assertGreaterEqual(len(d['etapas']),3)
                self.assertGreaterEqual(len(d['documentos']),1)
                self.assertIn('não oficial',d['aviso'])
                self.assertTrue(d['fontes'])

    def test_simulador_rejeita_entrada_invalida(self):
        for vals in [('inexistente','consulta','digital'),('cpf','falso','digital'),('cpf','consulta','QR'),(None,'consulta','digital')]:
            with self.subTest(vals=vals),self.assertRaises(ValueError):
                simular(CATALOGO,*vals)

    def test_indicadores_sem_dados_pessoais_e_sem_metricas_inventadas(self):
        with tempfile.TemporaryDirectory() as pasta:
            destino=Path(pasta)/'metricas.csv'
            with patch('src.metricas.DESTINO',destino):
                d=relatorio(CATALOGO,PERGUNTAS_AVALIACAO)
                self.assertEqual(d['consultas_concluidas'],0)
                self.assertIsNone(d['tempo_medio_ms'])
                self.assertIsNone(d['percentual_util'])
                self.assertEqual(d['avaliacao_regras']['total'],len(PERGUNTAS_AVALIACAO))
                self.assertGreater(d['avaliacao_regras']['percentual'],0)
                registrar('sucesso',servico='cpf',tempo_ms=950)
                registrar('avaliacao',avaliacao='util')
                registrar('simulador',servico='cpf')
                d=relatorio(CATALOGO,PERGUNTAS_AVALIACAO)
                self.assertEqual(d['consultas_concluidas'],1)
                self.assertEqual(d['tempo_medio_ms'],950)
                self.assertEqual(d['avaliacoes_uteis'],1)
                self.assertEqual(d['eventos']['simulador'],1)
                conteudo=destino.read_text(encoding='utf-8')
                self.assertNotIn('Como emitir CPF',conteudo)


class RotasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Atendimento)
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close()

    def get(self,path):
        try:
            with urllib.request.urlopen(self.base+path,timeout=5) as r:
                return r.status, r.headers.get('Content-Type'),r.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            return e.code,e.headers.get('Content-Type'),e.read().decode('utf-8')

    def post(self,path,payload):
        req=urllib.request.Request(self.base+path,data=json.dumps(payload).encode('utf-8'),method='POST',headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=5) as r:
                return r.status,json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code,json.loads(e.read())

    def test_todas_as_sete_paginas_recarregam(self):
        for caminho in ('/','/servicos','/assistente','/guias','/simulador','/indicadores','/transparencia'):
            with self.subTest(caminho=caminho):
                status,tipo,corpo=self.get(caminho)
                self.assertEqual(status,200)
                self.assertIn('text/html',tipo)
                self.assertIn('Cidadão Fácil',corpo)
                self.assertIn(f'data-page="{caminho}"',corpo)

    def test_arquivos_estaticos(self):
        for caminho in ('/static/app.js','/static/style.css'):
            code,content_type,body=self.get(caminho)
            self.assertEqual(code,200)
            self.assertGreater(len(body),1000)

    def test_catalogo_detalhe_e_nao_existe(self):
        code,_,content=self.get('/api/servicos')
        self.assertEqual(code,200)
        self.assertEqual(len(json.loads(content)),7)
        code,_,content=self.get('/api/servicos/cpf')
        self.assertEqual(code,200)
        self.assertIn('orientacoes',json.loads(content))
        code,_,content=self.get('/api/servicos/inexistente')
        self.assertEqual(code,404)

    def test_simulador_api_e_erros(self):
        code,data=self.post('/api/simular',{'servico':'cpf','situacao':'consulta','modalidade':'digital'})
        self.assertEqual(code,200)
        self.assertEqual(data['servico'],'cpf')
        self.assertGreater(len(data['fontes']),0)
        code,data=self.post('/api/simular',{'servico':'cpf','situacao':'xxx','modalidade':'digital'})
        self.assertEqual(code,400)

    def test_indicadores_reais_api(self):
        code,_,body=self.get('/api/indicadores')
        self.assertEqual(code,200)
        data=json.loads(body)
        self.assertIn('tempo_medio_ms',data)
        self.assertIn('avaliacao_regras',data)
        self.assertNotIn('taxa_acerto_ia',data)

    def test_path_traversal_nao_abre_arquivos(self):
        status,_,_=self.get('/static/..%2F.env')
        self.assertEqual(status,404)


if __name__=='__main__':unittest.main()

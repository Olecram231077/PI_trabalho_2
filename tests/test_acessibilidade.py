from bs4 import BeautifulSoup


def obter_html(client, rota):
    resposta = client.get(rota)
    assert resposta.status_code == 200
    return BeautifulSoup(resposta.data, 'html.parser')


def test_pagina_tem_idioma_definido(client):
    sopa = obter_html(client, '/')
    assert sopa.html.get('lang') == 'pt-BR'


def test_pagina_tem_skip_link(client):
    sopa = obter_html(client, '/')
    skip = sopa.find('a', class_='skip-link')
    assert skip is not None
    assert skip.get('href') == '#conteudo-principal'


def test_pagina_tem_landmarks(client):
    sopa = obter_html(client, '/')
    assert sopa.find('header') is not None
    assert sopa.find('main') is not None
    assert sopa.find('footer') is not None
    assert sopa.find('nav') is not None


def test_nav_tem_rotulo_acessivel(client):
    sopa = obter_html(client, '/')
    nav = sopa.find('nav')
    assert nav.get('aria-label') is not None


def test_regiao_de_anuncios_existe(client):
    sopa = obter_html(client, '/')
    regiao = sopa.find(id='regiao-anuncios')
    assert regiao is not None
    assert regiao.get('aria-live') == 'polite'


def test_tabelas_tem_caption(client):
    for rota in ('/professores', '/disciplinas', '/substituicoes'):
        sopa = obter_html(client, rota)
        tabela = sopa.find('table')
        assert tabela is not None
        assert tabela.find('caption') is not None
        assert tabela.find('th', attrs={'scope': 'col'}) is not None


def test_formulario_professor_tem_labels(client):
    sopa = obter_html(client, '/professores/novo')

    for campo_id in ('nome', 'email', 'telefone', 'especialidade', 'cep'):
        campo = sopa.find(id=campo_id)
        assert campo is not None, f'Campo {campo_id} não encontrado'
        label = sopa.find('label', attrs={'for': campo_id})
        assert label is not None, f'Label ausente para {campo_id}'


def test_campos_obrigatorios_marcados(client):
    sopa = obter_html(client, '/professores/novo')

    for campo_id in ('nome', 'email'):
        campo = sopa.find(id=campo_id)
        assert campo.get('required') is not None
        assert campo.get('aria-required') == 'true'


def test_formulario_substituicao_tem_labels(client):
    sopa = obter_html(client, '/substituicoes/nova')

    for campo_id in ('professor_titular_id', 'professor_substituto_id',
                     'disciplina_id', 'data_inicio', 'data_fim'):
        campo = sopa.find(id=campo_id)
        assert campo is not None, f'Campo {campo_id} não encontrado'
        label = sopa.find('label', attrs={'for': campo_id})
        assert label is not None, f'Label ausente para {campo_id}'


def test_botao_menu_tem_aria_expanded(client):
    sopa = obter_html(client, '/')
    botao = sopa.find('button', class_='navbar-toggler')
    assert botao.get('aria-expanded') is not None
    assert botao.get('aria-label') is not None
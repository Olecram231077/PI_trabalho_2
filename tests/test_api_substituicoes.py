def criar_base(client):
    titular = client.post('/api/professores', json={
        'nome': 'Titular Teste', 'email': 'titular@escola.com'
    }).get_json()
    substituto = client.post('/api/professores', json={
        'nome': 'Substituto Teste', 'email': 'substituto@escola.com'
    }).get_json()
    disciplina = client.post('/api/disciplinas', json={'nome': 'Disciplina Teste'}).get_json()
    return titular, substituto, disciplina


def test_criar_substituicao(client):
    titular, substituto, disciplina = criar_base(client)

    resposta = client.post('/api/substituicoes', json={
        'professor_titular_id': titular['id'],
        'professor_substituto_id': substituto['id'],
        'disciplina_id': disciplina['id'],
        'data_inicio': '2026-11-01',
        'data_fim': '2026-11-15',
        'motivo': 'Licença médica',
    })
    assert resposta.status_code == 201
    dados = resposta.get_json()
    assert dados['professor_titular']['nome'] == 'Titular Teste'
    assert dados['data_inicio'] == '2026-11-01'


def test_substituicao_mesmo_professor(client):
    titular, _, disciplina = criar_base(client)

    resposta = client.post('/api/substituicoes', json={
        'professor_titular_id': titular['id'],
        'professor_substituto_id': titular['id'],
        'disciplina_id': disciplina['id'],
        'data_inicio': '2026-11-01',
    })
    assert resposta.status_code == 400
    assert resposta.get_json()['campo'] == 'professor_substituto_id'


def test_substituicao_sem_data_inicio(client):
    titular, substituto, disciplina = criar_base(client)

    resposta = client.post('/api/substituicoes', json={
        'professor_titular_id': titular['id'],
        'professor_substituto_id': substituto['id'],
        'disciplina_id': disciplina['id'],
    })
    assert resposta.status_code == 400
    assert resposta.get_json()['campo'] == 'data_inicio'


def test_substituicao_data_invalida(client):
    titular, substituto, disciplina = criar_base(client)

    resposta = client.post('/api/substituicoes', json={
        'professor_titular_id': titular['id'],
        'professor_substituto_id': substituto['id'],
        'disciplina_id': disciplina['id'],
        'data_inicio': '01/11/2026',
    })
    assert resposta.status_code == 400
    assert resposta.get_json()['campo'] == 'data_inicio'


def test_substituicao_data_fim_anterior(client):
    titular, substituto, disciplina = criar_base(client)

    resposta = client.post('/api/substituicoes', json={
        'professor_titular_id': titular['id'],
        'professor_substituto_id': substituto['id'],
        'disciplina_id': disciplina['id'],
        'data_inicio': '2026-11-15',
        'data_fim': '2026-11-01',
    })
    assert resposta.status_code == 400
    assert resposta.get_json()['campo'] == 'data_fim'


def test_remover_substituicao(client):
    titular, substituto, disciplina = criar_base(client)

    criada = client.post('/api/substituicoes', json={
        'professor_titular_id': titular['id'],
        'professor_substituto_id': substituto['id'],
        'disciplina_id': disciplina['id'],
        'data_inicio': '2026-11-01',
    }).get_json()

    resposta = client.delete(f"/api/substituicoes/{criada['id']}")
    assert resposta.status_code == 204


def test_nao_remover_professor_com_substituicao(client):
    titular, substituto, disciplina = criar_base(client)

    client.post('/api/substituicoes', json={
        'professor_titular_id': titular['id'],
        'professor_substituto_id': substituto['id'],
        'disciplina_id': disciplina['id'],
        'data_inicio': '2026-11-01',
    })

    resposta = client.delete(f"/api/professores/{titular['id']}")
    assert resposta.status_code == 409


def test_estatisticas(client):
    titular, substituto, disciplina = criar_base(client)

    client.post('/api/substituicoes', json={
        'professor_titular_id': titular['id'],
        'professor_substituto_id': substituto['id'],
        'disciplina_id': disciplina['id'],
        'data_inicio': '2026-11-01',
    })

    resposta = client.get('/api/estatisticas')
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert dados['totais']['professores'] == 2
    assert dados['totais']['disciplinas'] == 1
    assert dados['totais']['substituicoes'] == 1
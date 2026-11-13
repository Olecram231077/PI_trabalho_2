def test_listar_disciplinas_vazio(client):
    resposta = client.get('/api/disciplinas')
    assert resposta.status_code == 200
    assert resposta.get_json() == []


def test_criar_disciplina(client):
    resposta = client.post('/api/disciplinas', json={
        'nome': 'Matemática',
        'descricao': 'Álgebra e geometria',
        'carga_horaria': 80,
    })
    assert resposta.status_code == 201
    dados = resposta.get_json()
    assert dados['nome'] == 'Matemática'
    assert dados['carga_horaria'] == 80


def test_criar_disciplina_sem_nome(client):
    resposta = client.post('/api/disciplinas', json={'carga_horaria': 60})
    assert resposta.status_code == 400
    assert resposta.get_json()['campo'] == 'nome'


def test_criar_disciplina_nome_duplicado(client):
    client.post('/api/disciplinas', json={'nome': 'História'})
    resposta = client.post('/api/disciplinas', json={'nome': 'História'})
    assert resposta.status_code == 409


def test_criar_disciplina_carga_invalida(client):
    resposta = client.post('/api/disciplinas', json={'nome': 'Arte', 'carga_horaria': -10})
    assert resposta.status_code == 400
    assert resposta.get_json()['campo'] == 'carga_horaria'


def test_atualizar_disciplina(client):
    criada = client.post('/api/disciplinas', json={'nome': 'Geografia'}).get_json()

    resposta = client.put(f"/api/disciplinas/{criada['id']}", json={
        'carga_horaria': 60,
        'descricao': 'Geografia do Brasil',
    })
    assert resposta.status_code == 200
    assert resposta.get_json()['carga_horaria'] == 60


def test_remover_disciplina(client):
    criada = client.post('/api/disciplinas', json={'nome': 'Química'}).get_json()

    resposta = client.delete(f"/api/disciplinas/{criada['id']}")
    assert resposta.status_code == 204

    assert client.get(f"/api/disciplinas/{criada['id']}").status_code == 404


def test_remover_disciplina_inexistente(client):
    resposta = client.delete('/api/disciplinas/9999')
    assert resposta.status_code == 404
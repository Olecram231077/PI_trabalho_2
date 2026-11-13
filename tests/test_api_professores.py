def test_listar_professores_vazio(client):
    resposta = client.get('/api/professores')
    assert resposta.status_code == 200
    assert resposta.get_json() == []


def test_criar_professor(client):
    resposta = client.post('/api/professores', json={
        'nome': 'Carlos Santos',
        'email': 'carlos@escola.com',
        'especialidade': 'Português',
    })
    assert resposta.status_code == 201
    dados = resposta.get_json()
    assert dados['nome'] == 'Carlos Santos'
    assert dados['email'] == 'carlos@escola.com'
    assert dados['id'] is not None


def test_criar_professor_sem_nome(client):
    resposta = client.post('/api/professores', json={'email': 'teste@escola.com'})
    assert resposta.status_code == 400
    assert resposta.get_json()['campo'] == 'nome'


def test_criar_professor_email_invalido(client):
    resposta = client.post('/api/professores', json={'nome': 'Teste', 'email': 'invalido'})
    assert resposta.status_code == 400
    assert resposta.get_json()['campo'] == 'email'


def test_criar_professor_email_duplicado(client):
    client.post('/api/professores', json={'nome': 'A', 'email': 'dup@escola.com'})
    resposta = client.post('/api/professores', json={'nome': 'B', 'email': 'dup@escola.com'})
    assert resposta.status_code == 409


def test_obter_professor(client):
    criado = client.post('/api/professores', json={
        'nome': 'Maria Souza', 'email': 'maria@escola.com'
    }).get_json()

    resposta = client.get(f"/api/professores/{criado['id']}")
    assert resposta.status_code == 200
    assert resposta.get_json()['nome'] == 'Maria Souza'


def test_obter_professor_inexistente(client):
    resposta = client.get('/api/professores/9999')
    assert resposta.status_code == 404


def test_atualizar_professor(client):
    criado = client.post('/api/professores', json={
        'nome': 'Pedro Lima', 'email': 'pedro@escola.com'
    }).get_json()

    resposta = client.put(f"/api/professores/{criado['id']}", json={
        'nome': 'Pedro Lima Junior', 'especialidade': 'História'
    })
    assert resposta.status_code == 200
    assert resposta.get_json()['nome'] == 'Pedro Lima Junior'
    assert resposta.get_json()['especialidade'] == 'História'


def test_remover_professor(client):
    criado = client.post('/api/professores', json={
        'nome': 'Julia Costa', 'email': 'julia@escola.com'
    }).get_json()

    resposta = client.delete(f"/api/professores/{criado['id']}")
    assert resposta.status_code == 204

    assert client.get(f"/api/professores/{criado['id']}").status_code == 404


def test_busca_professor_por_nome(client):
    client.post('/api/professores', json={'nome': 'Ana Silva', 'email': 'ana@escola.com'})
    client.post('/api/professores', json={'nome': 'Bruno Costa', 'email': 'bruno@escola.com'})

    resposta = client.get('/api/professores?q=Ana')
    assert resposta.status_code == 200
    assert len(resposta.get_json()) == 1
    assert resposta.get_json()[0]['nome'] == 'Ana Silva'


def test_associar_disciplinas_ao_professor(client):
    disciplina = client.post('/api/disciplinas', json={'nome': 'Física'}).get_json()

    resposta = client.post('/api/professores', json={
        'nome': 'Rita Alves',
        'email': 'rita@escola.com',
        'disciplinas': [disciplina['id']],
    })
    assert resposta.status_code == 201
    assert len(resposta.get_json()['disciplinas']) == 1
    assert resposta.get_json()['disciplinas'][0]['nome'] == 'Física'
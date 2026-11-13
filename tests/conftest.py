import pytest
from app import create_app, db as _db


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    with app.app_context():
        _db.drop_all()
        _db.create_all()
        yield _db
        _db.session.remove()


@pytest.fixture()
def professor_exemplo(db):
    from app.models import Professor
    professor = Professor(nome='Ana Oliveira', email='ana@escola.com', especialidade='Matemática')
    db.session.add(professor)
    db.session.commit()
    return professor


@pytest.fixture()
def disciplina_exemplo(db):
    from app.models import Disciplina
    disciplina = Disciplina(nome='Matemática', carga_horaria=80)
    db.session.add(disciplina)
    db.session.commit()
    return disciplina
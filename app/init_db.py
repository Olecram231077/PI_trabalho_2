from app import create_app, db
from app import models  # noqa: F401 — registra os modelos

app = create_app()

with app.app_context():
    db.create_all()
    print('Tabelas criadas com sucesso.')
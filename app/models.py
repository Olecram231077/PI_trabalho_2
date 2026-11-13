from datetime import datetime
from app import db


professor_disciplina = db.Table(
    'professor_disciplina',
    db.Column('professor_id', db.Integer, db.ForeignKey('professores.id', ondelete='CASCADE'), primary_key=True),
    db.Column('disciplina_id', db.Integer, db.ForeignKey('disciplinas.id', ondelete='CASCADE'), primary_key=True),
)


class Professor(db.Model):
    __tablename__ = 'professores'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    telefone = db.Column(db.String(20))
    cep = db.Column(db.String(9))
    logradouro = db.Column(db.String(150))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    especialidade = db.Column(db.String(120))
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    disciplinas = db.relationship(
        'Disciplina',
        secondary=professor_disciplina,
        back_populates='professores',
        lazy='selectin'
    )

    def to_dict(self, incluir_disciplinas=True):
        dados = {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'cep': self.cep,
            'logradouro': self.logradouro,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'uf': self.uf,
            'especialidade': self.especialidade,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
        }
        if incluir_disciplinas:
            dados['disciplinas'] = [
                {'id': d.id, 'nome': d.nome} for d in self.disciplinas
            ]
        return dados


class Disciplina(db.Model):
    __tablename__ = 'disciplinas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, unique=True, index=True)
    descricao = db.Column(db.Text)
    carga_horaria = db.Column(db.Integer)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    professores = db.relationship(
        'Professor',
        secondary=professor_disciplina,
        back_populates='disciplinas',
        lazy='selectin'
    )

    def to_dict(self, incluir_professores=True):
        dados = {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'carga_horaria': self.carga_horaria,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
        }
        if incluir_professores:
            dados['professores'] = [
                {'id': p.id, 'nome': p.nome} for p in self.professores
            ]
        return dados


class Substituicao(db.Model):
    __tablename__ = 'substituicoes'

    id = db.Column(db.Integer, primary_key=True)
    professor_titular_id = db.Column(db.Integer, db.ForeignKey('professores.id', ondelete='CASCADE'), nullable=False)
    professor_substituto_id = db.Column(db.Integer, db.ForeignKey('professores.id', ondelete='CASCADE'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplinas.id', ondelete='CASCADE'), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date)
    motivo = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    professor_titular = db.relationship('Professor', foreign_keys=[professor_titular_id], lazy='joined')
    professor_substituto = db.relationship('Professor', foreign_keys=[professor_substituto_id], lazy='joined')
    disciplina = db.relationship('Disciplina', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'professor_titular': {'id': self.professor_titular.id, 'nome': self.professor_titular.nome} if self.professor_titular else None,
            'professor_substituto': {'id': self.professor_substituto.id, 'nome': self.professor_substituto.nome} if self.professor_substituto else None,
            'disciplina': {'id': self.disciplina.id, 'nome': self.disciplina.nome} if self.disciplina else None,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'motivo': self.motivo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
        }
from datetime import datetime
import requests
from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app import db
from app.models import Professor, Disciplina, Substituicao

api_bp = Blueprint('api', __name__)


def erro(mensagem, status=400, campo=None):
    payload = {'erro': mensagem}
    if campo:
        payload['campo'] = campo
    return jsonify(payload), status


def validar_email(email):
    if not email or '@' not in email or '.' not in email.split('@')[-1]:
        return False
    return True


def parse_data(valor, campo):
    if not valor:
        return None, None
    try:
        return datetime.strptime(valor, '%Y-%m-%d').date(), None
    except (ValueError, TypeError):
        return None, f'{campo} deve estar no formato AAAA-MM-DD'


@api_bp.route('/professores', methods=['GET'])
def listar_professores():
    busca = request.args.get('q', '').strip()
    query = Professor.query
    if busca:
        query = query.filter(Professor.nome.ilike(f'%{busca}%'))
    professores = query.order_by(Professor.nome).all()
    return jsonify([p.to_dict() for p in professores]), 200


@api_bp.route('/professores/<int:professor_id>', methods=['GET'])
def obter_professor(professor_id):
    professor = db.session.get(Professor, professor_id)
    if not professor:
        return erro('Professor não encontrado', 404)
    return jsonify(professor.to_dict()), 200


@api_bp.route('/professores', methods=['POST'])
def criar_professor():
    dados = request.get_json(silent=True) or {}

    nome = (dados.get('nome') or '').strip()
    email = (dados.get('email') or '').strip().lower()

    if not nome:
        return erro('O nome é obrigatório', 400, 'nome')
    if not validar_email(email):
        return erro('E-mail inválido', 400, 'email')

    if Professor.query.filter(func.lower(Professor.email) == email).first():
        return erro('Já existe um professor com este e-mail', 409, 'email')

    professor = Professor(
        nome=nome,
        email=email,
        telefone=(dados.get('telefone') or '').strip() or None,
        cep=(dados.get('cep') or '').strip() or None,
        logradouro=(dados.get('logradouro') or '').strip() or None,
        bairro=(dados.get('bairro') or '').strip() or None,
        cidade=(dados.get('cidade') or '').strip() or None,
        uf=(dados.get('uf') or '').strip().upper() or None,
        especialidade=(dados.get('especialidade') or '').strip() or None,
    )

    ids_disciplinas = dados.get('disciplinas') or []
    if ids_disciplinas:
        professor.disciplinas = Disciplina.query.filter(Disciplina.id.in_(ids_disciplinas)).all()

    try:
        db.session.add(professor)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return erro('Não foi possível cadastrar: dados duplicados', 409)

    return jsonify(professor.to_dict()), 201


@api_bp.route('/professores/<int:professor_id>', methods=['PUT'])
def atualizar_professor(professor_id):
    professor = db.session.get(Professor, professor_id)
    if not professor:
        return erro('Professor não encontrado', 404)

    dados = request.get_json(silent=True) or {}

    if 'nome' in dados:
        nome = (dados.get('nome') or '').strip()
        if not nome:
            return erro('O nome é obrigatório', 400, 'nome')
        professor.nome = nome

    if 'email' in dados:
        email = (dados.get('email') or '').strip().lower()
        if not validar_email(email):
            return erro('E-mail inválido', 400, 'email')
        existente = Professor.query.filter(
            func.lower(Professor.email) == email,
            Professor.id != professor_id
        ).first()
        if existente:
            return erro('Já existe outro professor com este e-mail', 409, 'email')
        professor.email = email

    for campo in ('telefone', 'cep', 'logradouro', 'bairro', 'cidade', 'especialidade'):
        if campo in dados:
            valor = (dados.get(campo) or '').strip()
            setattr(professor, campo, valor or None)

    if 'uf' in dados:
        professor.uf = (dados.get('uf') or '').strip().upper() or None

    if 'ativo' in dados:
        professor.ativo = bool(dados.get('ativo'))

    if 'disciplinas' in dados:
        ids = dados.get('disciplinas') or []
        professor.disciplinas = Disciplina.query.filter(Disciplina.id.in_(ids)).all() if ids else []

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return erro('Não foi possível atualizar: dados duplicados', 409)

    return jsonify(professor.to_dict()), 200


@api_bp.route('/professores/<int:professor_id>', methods=['DELETE'])
def remover_professor(professor_id):
    professor = db.session.get(Professor, professor_id)
    if not professor:
        return erro('Professor não encontrado', 404)

    em_uso = Substituicao.query.filter(
        (Substituicao.professor_titular_id == professor_id) |
        (Substituicao.professor_substituto_id == professor_id)
    ).first()
    if em_uso:
        return erro('Professor possui substituições registradas e não pode ser removido', 409)

    db.session.delete(professor)
    db.session.commit()
    return '', 204


@api_bp.route('/disciplinas', methods=['GET'])
def listar_disciplinas():
    disciplinas = Disciplina.query.order_by(Disciplina.nome).all()
    return jsonify([d.to_dict() for d in disciplinas]), 200


@api_bp.route('/disciplinas/<int:disciplina_id>', methods=['GET'])
def obter_disciplina(disciplina_id):
    disciplina = db.session.get(Disciplina, disciplina_id)
    if not disciplina:
        return erro('Disciplina não encontrada', 404)
    return jsonify(disciplina.to_dict()), 200


@api_bp.route('/disciplinas', methods=['POST'])
def criar_disciplina():
    dados = request.get_json(silent=True) or {}

    nome = (dados.get('nome') or '').strip()
    if not nome:
        return erro('O nome da disciplina é obrigatório', 400, 'nome')

    if Disciplina.query.filter(func.lower(Disciplina.nome) == nome.lower()).first():
        return erro('Já existe uma disciplina com este nome', 409, 'nome')

    carga = dados.get('carga_horaria')
    if carga not in (None, ''):
        try:
            carga = int(carga)
            if carga <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return erro('Carga horária deve ser um número inteiro positivo', 400, 'carga_horaria')
    else:
        carga = None

    disciplina = Disciplina(
        nome=nome,
        descricao=(dados.get('descricao') or '').strip() or None,
        carga_horaria=carga,
    )

    db.session.add(disciplina)
    db.session.commit()
    return jsonify(disciplina.to_dict()), 201


@api_bp.route('/disciplinas/<int:disciplina_id>', methods=['PUT'])
def atualizar_disciplina(disciplina_id):
    disciplina = db.session.get(Disciplina, disciplina_id)
    if not disciplina:
        return erro('Disciplina não encontrada', 404)

    dados = request.get_json(silent=True) or {}

    if 'nome' in dados:
        nome = (dados.get('nome') or '').strip()
        if not nome:
            return erro('O nome da disciplina é obrigatório', 400, 'nome')
        existente = Disciplina.query.filter(
            func.lower(Disciplina.nome) == nome.lower(),
            Disciplina.id != disciplina_id
        ).first()
        if existente:
            return erro('Já existe outra disciplina com este nome', 409, 'nome')
        disciplina.nome = nome

    if 'descricao' in dados:
        disciplina.descricao = (dados.get('descricao') or '').strip() or None

    if 'carga_horaria' in dados:
        carga = dados.get('carga_horaria')
        if carga in (None, ''):
            disciplina.carga_horaria = None
        else:
            try:
                carga = int(carga)
                if carga <= 0:
                    raise ValueError
                disciplina.carga_horaria = carga
            except (ValueError, TypeError):
                return erro('Carga horária deve ser um número inteiro positivo', 400, 'carga_horaria')

    db.session.commit()
    return jsonify(disciplina.to_dict()), 200


@api_bp.route('/disciplinas/<int:disciplina_id>', methods=['DELETE'])
def remover_disciplina(disciplina_id):
    disciplina = db.session.get(Disciplina, disciplina_id)
    if not disciplina:
        return erro('Disciplina não encontrada', 404)

    if Substituicao.query.filter_by(disciplina_id=disciplina_id).first():
        return erro('Disciplina possui substituições registradas e não pode ser removida', 409)

    db.session.delete(disciplina)
    db.session.commit()
    return '', 204


@api_bp.route('/substituicoes', methods=['GET'])
def listar_substituicoes():
    substituicoes = Substituicao.query.order_by(Substituicao.data_inicio.desc()).all()
    return jsonify([s.to_dict() for s in substituicoes]), 200


@api_bp.route('/substituicoes', methods=['POST'])
def criar_substituicao():
    dados = request.get_json(silent=True) or {}

    try:
        titular_id = int(dados.get('professor_titular_id'))
        substituto_id = int(dados.get('professor_substituto_id'))
        disciplina_id = int(dados.get('disciplina_id'))
    except (TypeError, ValueError):
        return erro('Professor titular, substituto e disciplina são obrigatórios', 400)

    if titular_id == substituto_id:
        return erro('O professor substituto deve ser diferente do titular', 400, 'professor_substituto_id')

    if not db.session.get(Professor, titular_id):
        return erro('Professor titular não encontrado', 404, 'professor_titular_id')
    if not db.session.get(Professor, substituto_id):
        return erro('Professor substituto não encontrado', 404, 'professor_substituto_id')
    if not db.session.get(Disciplina, disciplina_id):
        return erro('Disciplina não encontrada', 404, 'disciplina_id')

    data_inicio, msg = parse_data(dados.get('data_inicio'), 'Data de início')
    if msg:
        return erro(msg, 400, 'data_inicio')
    if not data_inicio:
        return erro('A data de início é obrigatória', 400, 'data_inicio')

    data_fim, msg = parse_data(dados.get('data_fim'), 'Data de fim')
    if msg:
        return erro(msg, 400, 'data_fim')

    if data_fim and data_fim < data_inicio:
        return erro('A data de fim não pode ser anterior à data de início', 400, 'data_fim')

    substituicao = Substituicao(
        professor_titular_id=titular_id,
        professor_substituto_id=substituto_id,
        disciplina_id=disciplina_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        motivo=(dados.get('motivo') or '').strip() or None,
    )

    db.session.add(substituicao)
    db.session.commit()
    return jsonify(substituicao.to_dict()), 201


@api_bp.route('/substituicoes/<int:substituicao_id>', methods=['DELETE'])
def remover_substituicao(substituicao_id):
    substituicao = db.session.get(Substituicao, substituicao_id)
    if not substituicao:
        return erro('Substituição não encontrada', 404)

    db.session.delete(substituicao)
    db.session.commit()
    return '', 204


@api_bp.route('/cep/<cep>', methods=['GET'])
def consultar_cep(cep):
    cep_limpo = ''.join(filter(str.isdigit, cep or ''))

    if len(cep_limpo) != 8:
        return erro('CEP deve conter 8 dígitos', 400, 'cep')

    base_url = current_app.config['VIACEP_BASE_URL']
    timeout = current_app.config['VIACEP_TIMEOUT']

    try:
        resposta = requests.get(f'{base_url}/{cep_limpo}/json/', timeout=timeout)
        resposta.raise_for_status()
        dados = resposta.json()
    except requests.Timeout:
        return erro('O serviço de CEP demorou demais para responder', 504)
    except requests.RequestException:
        return erro('Não foi possível consultar o serviço de CEP', 502)

    if dados.get('erro'):
        return erro('CEP não encontrado', 404, 'cep')

    return jsonify({
        'cep': dados.get('cep'),
        'logradouro': dados.get('logradouro'),
        'complemento': dados.get('complemento'),
        'bairro': dados.get('bairro'),
        'cidade': dados.get('localidade'),
        'uf': dados.get('uf'),
    }), 200


@api_bp.route('/estatisticas', methods=['GET'])
def estatisticas():
    total_professores = Professor.query.count()
    total_disciplinas = Disciplina.query.count()
    total_substituicoes = Substituicao.query.count()

    por_disciplina = (
        db.session.query(Disciplina.nome, func.count(Substituicao.id))
        .join(Substituicao, Substituicao.disciplina_id == Disciplina.id)
        .group_by(Disciplina.nome)
        .order_by(func.count(Substituicao.id).desc())
        .all()
    )

    if db.engine.dialect.name == 'postgresql':
        expressao_mes = func.to_char(Substituicao.data_inicio, 'YYYY-MM')
    else:
        expressao_mes = func.strftime('%Y-%m', Substituicao.data_inicio)

    por_mes = (
        db.session.query(expressao_mes, func.count(Substituicao.id))
        .group_by(expressao_mes)
        .order_by(expressao_mes)
        .all()
    )

    return jsonify({
        'totais': {
            'professores': total_professores,
            'disciplinas': total_disciplinas,
            'substituicoes': total_substituicoes,
        },
        'substituicoes_por_disciplina': [
            {'disciplina': nome, 'quantidade': qtd} for nome, qtd in por_disciplina
        ],
        'substituicoes_por_mes': [
            {'mes': mes, 'quantidade': qtd} for mes, qtd in por_mes
        ],
    }), 200
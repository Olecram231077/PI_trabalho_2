from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)


@views_bp.route('/')
def index():
    return render_template('index.html')


@views_bp.route('/professores')
def professores():
    return render_template('professores/listar.html')


@views_bp.route('/professores/novo')
def professor_novo():
    return render_template('professores/form.html', professor_id=None)


@views_bp.route('/professores/<int:professor_id>/editar')
def professor_editar(professor_id):
    return render_template('professores/form.html', professor_id=professor_id)


@views_bp.route('/disciplinas')
def disciplinas():
    return render_template('disciplinas/listar.html')


@views_bp.route('/disciplinas/nova')
def disciplina_nova():
    return render_template('disciplinas/form.html', disciplina_id=None)


@views_bp.route('/disciplinas/<int:disciplina_id>/editar')
def disciplina_editar(disciplina_id):
    return render_template('disciplinas/form.html', disciplina_id=disciplina_id)


@views_bp.route('/substituicoes')
def substituicoes():
    return render_template('substituicoes/listar.html')


@views_bp.route('/substituicoes/nova')
def substituicao_nova():
    return render_template('substituicoes/form.html')
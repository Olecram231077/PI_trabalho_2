/* Lógica das telas: CRUD via Fetch API, sem recarregar a página. */

document.addEventListener('DOMContentLoaded', () => {
  const pagina = document.body.dataset.pagina;

  if (pagina === 'dashboard') iniciarDashboard();
  if (pagina === 'professores-lista') iniciarListaProfessores();
  if (pagina === 'professor-form') iniciarFormProfessor();
  if (pagina === 'disciplinas-lista') iniciarListaDisciplinas();
  if (pagina === 'disciplina-form') iniciarFormDisciplina();
  if (pagina === 'substituicoes-lista') iniciarListaSubstituicoes();
  if (pagina === 'substituicao-form') iniciarFormSubstituicao();
});

function criarCelula(texto) {
  const td = document.createElement('td');
  td.textContent = texto ?? '—';
  return td;
}

function criarBotao(rotulo, classe, aoClicar, rotuloAcessivel) {
  const botao = document.createElement('button');
  botao.type = 'button';
  botao.className = classe;
  botao.textContent = rotulo;
  if (rotuloAcessivel) botao.setAttribute('aria-label', rotuloAcessivel);
  botao.addEventListener('click', aoClicar);
  return botao;
}

function exibirAlerta(container, mensagem, tipo = 'success') {
  container.innerHTML = '';
  const alerta = document.createElement('div');
  alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
  alerta.setAttribute('role', 'alert');
  alerta.textContent = mensagem;

  const fechar = document.createElement('button');
  fechar.type = 'button';
  fechar.className = 'btn-close';
  fechar.setAttribute('data-bs-dismiss', 'alert');
  fechar.setAttribute('aria-label', 'Fechar mensagem');
  alerta.appendChild(fechar);

  container.appendChild(alerta);
  A11y.anunciar(mensagem, tipo === 'danger' ? 'assertive' : 'polite');
}

function formatarData(iso) {
  if (!iso) return '—';
  const [ano, mes, dia] = iso.split('-');
  return `${dia}/${mes}/${ano}`;
}

/* ---------- Dashboard ---------- */

async function iniciarDashboard() {
  try {
    const dados = await API.estatisticas.obter();

    document.getElementById('total-professores').textContent = dados.totais.professores;
    document.getElementById('total-disciplinas').textContent = dados.totais.disciplinas;
    document.getElementById('total-substituicoes').textContent = dados.totais.substituicoes;

    desenharGraficoDisciplinas(dados.substituicoes_por_disciplina);
    desenharGraficoMeses(dados.substituicoes_por_mes);
  } catch (erro) {
    A11y.anunciar(`Erro ao carregar estatísticas: ${erro.message}`, 'assertive');
  }
}

function desenharGraficoDisciplinas(itens) {
  const canvas = document.getElementById('grafico-disciplinas');
  if (!canvas || typeof Chart === 'undefined') return;

  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: itens.map((i) => i.disciplina),
      datasets: [{
        label: 'Substituições',
        data: itens.map((i) => i.quantidade),
        backgroundColor: 'rgba(13, 110, 253, 0.7)',
        borderColor: 'rgba(13, 110, 253, 1)',
        borderWidth: 1,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
    },
  });
}

function desenharGraficoMeses(itens) {
  const canvas = document.getElementById('grafico-meses');
  if (!canvas || typeof Chart === 'undefined') return;

  new Chart(canvas, {
    type: 'line',
    data: {
      labels: itens.map((i) => i.mes),
      datasets: [{
        label: 'Substituições por mês',
        data: itens.map((i) => i.quantidade),
        borderColor: 'rgba(25, 135, 84, 1)',
        backgroundColor: 'rgba(25, 135, 84, 0.2)',
        fill: true,
        tension: 0.3,
      }],
    },
    options: {
      responsive: true,
      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
    },
  });
}

/* ---------- Professores: lista ---------- */

async function iniciarListaProfessores() {
  const corpo = document.getElementById('corpo-tabela');
  const alertas = document.getElementById('area-alertas');
  const campoBusca = document.getElementById('campo-busca');

  async function carregar(busca = '') {
    corpo.innerHTML = '';
    try {
      const professores = await API.professores.listar(busca);

      if (!professores.length) {
        const linha = document.createElement('tr');
        const celula = document.createElement('td');
        celula.colSpan = 5;
        celula.className = 'text-center text-muted py-4';
        celula.textContent = busca
          ? 'Nenhum professor encontrado para esta busca.'
          : 'Nenhum professor cadastrado ainda.';
        linha.appendChild(celula);
        corpo.appendChild(linha);
        return;
      }

      professores.forEach((p) => {
        const linha = document.createElement('tr');

        linha.appendChild(criarCelula(p.nome));
        linha.appendChild(criarCelula(p.email));
        linha.appendChild(criarCelula(p.especialidade));
        linha.appendChild(criarCelula(
          p.disciplinas && p.disciplinas.length
            ? p.disciplinas.map((d) => d.nome).join(', ')
            : '—'
        ));

        const acoes = document.createElement('td');
        const grupo = document.createElement('div');
        grupo.className = 'btn-group btn-group-sm';
        grupo.setAttribute('role', 'group');

        const editar = document.createElement('a');
        editar.href = `/professores/${p.id}/editar`;
        editar.className = 'btn btn-outline-primary';
        editar.textContent = 'Editar';
        editar.setAttribute('aria-label', `Editar professor ${p.nome}`);

        const remover = criarBotao(
          'Excluir',
          'btn btn-outline-danger',
          async () => {
            if (!window.confirm(`Excluir o professor ${p.nome}?`)) return;
            try {
              await API.professores.remover(p.id);
              exibirAlerta(alertas, 'Professor excluído com sucesso.');
              carregar(campoBusca ? campoBusca.value : '');
            } catch (erro) {
              exibirAlerta(alertas, erro.message, 'danger');
            }
          },
          `Excluir professor ${p.nome}`
        );

        grupo.appendChild(editar);
        grupo.appendChild(remover);
        acoes.appendChild(grupo);
        linha.appendChild(acoes);

        corpo.appendChild(linha);
      });
    } catch (erro) {
      exibirAlerta(alertas, `Erro ao carregar professores: ${erro.message}`, 'danger');
    }
  }

  if (campoBusca) {
    let temporizador;
    campoBusca.addEventListener('input', () => {
      clearTimeout(temporizador);
      temporizador = setTimeout(() => carregar(campoBusca.value), 350);
    });
  }

  carregar();
}

/* ---------- Professor: formulário ---------- */

async function iniciarFormProfessor() {
  const form = document.getElementById('form-professor');
  const alertas = document.getElementById('area-alertas');
  const professorId = form.dataset.professorId || null;
  const containerDisciplinas = document.getElementById('lista-disciplinas');
  const campoCep = document.getElementById('cep');

  try {
    const disciplinas = await API.disciplinas.listar();

    if (!disciplinas.length) {
      containerDisciplinas.innerHTML = '<p class="text-muted mb-0">Nenhuma disciplina cadastrada.</p>';
    } else {
      disciplinas.forEach((d) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'form-check';

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.className = 'form-check-input';
        input.id = `disciplina-${d.id}`;
        input.value = d.id;

        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `disciplina-${d.id}`;
        label.textContent = d.nome;

        wrapper.appendChild(input);
        wrapper.appendChild(label);
        containerDisciplinas.appendChild(wrapper);
      });
    }

    if (professorId) {
      const professor = await API.professores.obter(professorId);

      document.getElementById('nome').value = professor.nome || '';
      document.getElementById('email').value = professor.email || '';
      document.getElementById('telefone').value = professor.telefone || '';
      document.getElementById('especialidade').value = professor.especialidade || '';
      document.getElementById('cep').value = professor.cep || '';
      document.getElementById('logradouro').value = professor.logradouro || '';
      document.getElementById('bairro').value = professor.bairro || '';
      document.getElementById('cidade').value = professor.cidade || '';
      document.getElementById('uf').value = professor.uf || '';

      (professor.disciplinas || []).forEach((d) => {
        const checkbox = document.getElementById(`disciplina-${d.id}`);
        if (checkbox) checkbox.checked = true;
      });

      document.getElementById('titulo-form').textContent = `Editar professor: ${professor.nome}`;
    }
  } catch (erro) {
    exibirAlerta(alertas, `Erro ao carregar dados: ${erro.message}`, 'danger');
  }

  if (campoCep) {
    campoCep.addEventListener('blur', async () => {
      const cep = campoCep.value.replace(/\D/g, '');
      if (cep.length !== 8) return;

      try {
        const dados = await API.cep.consultar(cep);
        document.getElementById('logradouro').value = dados.logradouro || '';
        document.getElementById('bairro').value = dados.bairro || '';
        document.getElementById('cidade').value = dados.cidade || '';
        document.getElementById('uf').value = dados.uf || '';
        A11y.anunciar('Endereço preenchido automaticamente pelo CEP.');
      } catch (erro) {
        A11y.anunciar(`Não foi possível buscar o CEP: ${erro.message}`, 'assertive');
      }
    });
  }

  form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    A11y.limparTodosErros(form);

    const dados = {
      nome: document.getElementById('nome').value.trim(),
      email: document.getElementById('email').value.trim(),
      telefone: document.getElementById('telefone').value.trim(),
      especialidade: document.getElementById('especialidade').value.trim(),
      cep: document.getElementById('cep').value.trim(),
      logradouro: document.getElementById('logradouro').value.trim(),
      bairro: document.getElementById('bairro').value.trim(),
      cidade: document.getElementById('cidade').value.trim(),
      uf: document.getElementById('uf').value.trim(),
      disciplinas: Array.from(
        containerDisciplinas.querySelectorAll('input[type="checkbox"]:checked')
      ).map((c) => Number(c.value)),
    };

    let valido = true;
    if (!dados.nome) {
      A11y.marcarErro('nome', 'Informe o nome do professor.');
      valido = false;
    }
    if (!dados.email || !dados.email.includes('@')) {
      A11y.marcarErro('email', 'Informe um e-mail válido.');
      valido = false;
    }
    if (!valido) {
      A11y.anunciar('Existem campos com erro no formulário.', 'assertive');
      return;
    }

    try {
      if (professorId) {
        await API.professores.atualizar(professorId, dados);
        exibirAlerta(alertas, 'Professor atualizado com sucesso.');
      } else {
        await API.professores.criar(dados);
        exibirAlerta(alertas, 'Professor cadastrado com sucesso.');
        form.reset();
      }
      window.setTimeout(() => { window.location.href = '/professores'; }, 1200);
    } catch (erro) {
      if (erro.campo) A11y.marcarErro(erro.campo, erro.message);
      exibirAlerta(alertas, erro.message, 'danger');
    }
  });
}

/* ---------- Disciplinas: lista ---------- */

async function iniciarListaDisciplinas() {
  const corpo = document.getElementById('corpo-tabela');
  const alertas = document.getElementById('area-alertas');

  async function carregar() {
    corpo.innerHTML = '';
    try {
      const disciplinas = await API.disciplinas.listar();

      if (!disciplinas.length) {
        const linha = document.createElement('tr');
        const celula = document.createElement('td');
        celula.colSpan = 5;
        celula.className = 'text-center text-muted py-4';
        celula.textContent = 'Nenhuma disciplina cadastrada ainda.';
        linha.appendChild(celula);
        corpo.appendChild(linha);
        return;
      }

      disciplinas.forEach((d) => {
        const linha = document.createElement('tr');
        linha.appendChild(criarCelula(d.nome));
        linha.appendChild(criarCelula(d.descricao));
        linha.appendChild(criarCelula(d.carga_horaria ? `${d.carga_horaria}h` : '—'));
        linha.appendChild(criarCelula(
          d.professores && d.professores.length
            ? d.professores.map((p) => p.nome).join(', ')
            : '—'
        ));

        const acoes = document.createElement('td');
        const grupo = document.createElement('div');
        grupo.className = 'btn-group btn-group-sm';
        grupo.setAttribute('role', 'group');

        const editar = document.createElement('a');
        editar.href = `/disciplinas/${d.id}/editar`;
        editar.className = 'btn btn-outline-primary';
        editar.textContent = 'Editar';
        editar.setAttribute('aria-label', `Editar disciplina ${d.nome}`);

        const remover = criarBotao(
          'Excluir',
          'btn btn-outline-danger',
          async () => {
            if (!window.confirm(`Excluir a disciplina ${d.nome}?`)) return;
            try {
              await API.disciplinas.remover(d.id);
              exibirAlerta(alertas, 'Disciplina excluída com sucesso.');
              carregar();
            } catch (erro) {
              exibirAlerta(alertas, erro.message, 'danger');
            }
          },
          `Excluir disciplina ${d.nome}`
        );

        grupo.appendChild(editar);
        grupo.appendChild(remover);
        acoes.appendChild(grupo);
        linha.appendChild(acoes);

        corpo.appendChild(linha);
      });
    } catch (erro) {
      exibirAlerta(alertas, `Erro ao carregar disciplinas: ${erro.message}`, 'danger');
    }
  }

  carregar();
}

/* ---------- Disciplina: formulário ---------- */

async function iniciarFormDisciplina() {
  const form = document.getElementById('form-disciplina');
  const alertas = document.getElementById('area-alertas');
  const disciplinaId = form.dataset.disciplinaId || null;

  if (disciplinaId) {
    try {
      const disciplina = await API.disciplinas.obter(disciplinaId);
      document.getElementById('nome').value = disciplina.nome || '';
      document.getElementById('descricao').value = disciplina.descricao || '';
      document.getElementById('carga_horaria').value = disciplina.carga_horaria || '';
      document.getElementById('titulo-form').textContent = `Editar disciplina: ${disciplina.nome}`;
    } catch (erro) {
      exibirAlerta(alertas, `Erro ao carregar disciplina: ${erro.message}`, 'danger');
    }
  }

  form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    A11y.limparTodosErros(form);

    const dados = {
      nome: document.getElementById('nome').value.trim(),
      descricao: document.getElementById('descricao').value.trim(),
      carga_horaria: document.getElementById('carga_horaria').value || null,
    };

    if (!dados.nome) {
      A11y.marcarErro('nome', 'Informe o nome da disciplina.');
      A11y.anunciar('Existem campos com erro no formulário.', 'assertive');
      return;
    }

    try {
      if (disciplinaId) {
        await API.disciplinas.atualizar(disciplinaId, dados);
        exibirAlerta(alertas, 'Disciplina atualizada com sucesso.');
      } else {
        await API.disciplinas.criar(dados);
        exibirAlerta(alertas, 'Disciplina cadastrada com sucesso.');
        form.reset();
      }
      window.setTimeout(() => { window.location.href = '/disciplinas'; }, 1200);
    } catch (erro) {
      if (erro.campo) A11y.marcarErro(erro.campo, erro.message);
      exibirAlerta(alertas, erro.message, 'danger');
    }
  });
}

/* ---------- Substituições: lista ---------- */

async function iniciarListaSubstituicoes() {
  const corpo = document.getElementById('corpo-tabela');
  const alertas = document.getElementById('area-alertas');

  async function carregar() {
    corpo.innerHTML = '';
    try {
      const substituicoes = await API.substituicoes.listar();

      if (!substituicoes.length) {
        const linha = document.createElement('tr');
        const celula = document.createElement('td');
        celula.colSpan = 6;
        celula.className = 'text-center text-muted py-4';
        celula.textContent = 'Nenhuma substituição registrada ainda.';
        linha.appendChild(celula);
        corpo.appendChild(linha);
        return;
      }

      substituicoes.forEach((s) => {
        const linha = document.createElement('tr');
        linha.appendChild(criarCelula(s.professor_titular ? s.professor_titular.nome : '—'));
        linha.appendChild(criarCelula(s.professor_substituto ? s.professor_substituto.nome : '—'));
        linha.appendChild(criarCelula(s.disciplina ? s.disciplina.nome : '—'));
        linha.appendChild(criarCelula(formatarData(s.data_inicio)));
        linha.appendChild(criarCelula(formatarData(s.data_fim)));

        const acoes = document.createElement('td');
        const remover = criarBotao(
          'Excluir',
          'btn btn-outline-danger btn-sm',
          async () => {
            if (!window.confirm('Excluir esta substituição?')) return;
            try {
              await API.substituicoes.remover(s.id);
              exibirAlerta(alertas, 'Substituição excluída com sucesso.');
              carregar();
            } catch (erro) {
              exibirAlerta(alertas, erro.message, 'danger');
            }
          },
          'Excluir substituição'
        );
        acoes.appendChild(remover);
        linha.appendChild(acoes);

        corpo.appendChild(linha);
      });
    } catch (erro) {
      exibirAlerta(alertas, `Erro ao carregar substituições: ${erro.message}`, 'danger');
    }
  }

  carregar();
}

/* ---------- Substituição: formulário ---------- */

async function iniciarFormSubstituicao() {
  const form = document.getElementById('form-substituicao');
  const alertas = document.getElementById('area-alertas');
  const selectTitular = document.getElementById('professor_titular_id');
  const selectSubstituto = document.getElementById('professor_substituto_id');
  const selectDisciplina = document.getElementById('disciplina_id');

  try {
    const [professores, disciplinas] = await Promise.all([
      API.professores.listar(),
      API.disciplinas.listar(),
    ]);

    professores.forEach((p) => {
      [selectTitular, selectSubstituto].forEach((select) => {
        const opcao = document.createElement('option');
        opcao.value = p.id;
        opcao.textContent = p.nome;
        select.appendChild(opcao);
      });
    });

    disciplinas.forEach((d) => {
      const opcao = document.createElement('option');
      opcao.value = d.id;
      opcao.textContent = d.nome;
      selectDisciplina.appendChild(opcao);
    });
  } catch (erro) {
    exibirAlerta(alertas, `Erro ao carregar dados: ${erro.message}`, 'danger');
  }

  form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    A11y.limparTodosErros(form);

    const dados = {
      professor_titular_id: Number(selectTitular.value),
      professor_substituto_id: Number(selectSubstituto.value),
      disciplina_id: Number(selectDisciplina.value),
      data_inicio: document.getElementById('data_inicio').value,
      data_fim: document.getElementById('data_fim').value || null,
      motivo: document.getElementById('motivo').value.trim(),
    };

    let valido = true;
    if (!dados.professor_titular_id) {
      A11y.marcarErro('professor_titular_id', 'Selecione o professor titular.');
      valido = false;
    }
    if (!dados.professor_substituto_id) {
      A11y.marcarErro('professor_substituto_id', 'Selecione o professor substituto.');
      valido = false;
    }
    if (!dados.disciplina_id) {
      A11y.marcarErro('disciplina_id', 'Selecione a disciplina.');
      valido = false;
    }
    if (!dados.data_inicio) {
      A11y.marcarErro('data_inicio', 'Informe a data de início.');
      valido = false;
    }
    if (!valido) {
      A11y.anunciar('Existem campos com erro no formulário.', 'assertive');
      return;
    }

    try {
      await API.substituicoes.criar(dados);
      exibirAlerta(alertas, 'Substituição registrada com sucesso.');
      form.reset();
      window.setTimeout(() => { window.location.href = '/substituicoes'; }, 1200);
    } catch (erro) {
      if (erro.campo) A11y.marcarErro(erro.campo, erro.message);
      exibirAlerta(alertas, erro.message, 'danger');
    }
  });
}
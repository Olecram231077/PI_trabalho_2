/* Camada de acesso à API REST do sistema. */

const API = (() => {
  const BASE = '/api';

  async function requisitar(caminho, opcoes = {}) {
    const config = {
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      ...opcoes,
    };

    const resposta = await fetch(`${BASE}${caminho}`, config);

    if (resposta.status === 204) return null;

    let corpo = null;
    try {
      corpo = await resposta.json();
    } catch (e) {
      corpo = null;
    }

    if (!resposta.ok) {
      const mensagem = (corpo && corpo.erro) || `Erro ${resposta.status}`;
      const erro = new Error(mensagem);
      erro.status = resposta.status;
      erro.campo = corpo && corpo.campo;
      throw erro;
    }

    return corpo;
  }

  return {
    professores: {
      listar: (busca = '') => requisitar(`/professores${busca ? `?q=${encodeURIComponent(busca)}` : ''}`),
      obter: (id) => requisitar(`/professores/${id}`),
      criar: (dados) => requisitar('/professores', { method: 'POST', body: JSON.stringify(dados) }),
      atualizar: (id, dados) => requisitar(`/professores/${id}`, { method: 'PUT', body: JSON.stringify(dados) }),
      remover: (id) => requisitar(`/professores/${id}`, { method: 'DELETE' }),
    },
    disciplinas: {
      listar: () => requisitar('/disciplinas'),
      obter: (id) => requisitar(`/disciplinas/${id}`),
      criar: (dados) => requisitar('/disciplinas', { method: 'POST', body: JSON.stringify(dados) }),
      atualizar: (id, dados) => requisitar(`/disciplinas/${id}`, { method: 'PUT', body: JSON.stringify(dados) }),
      remover: (id) => requisitar(`/disciplinas/${id}`, { method: 'DELETE' }),
    },
    substituicoes: {
      listar: () => requisitar('/substituicoes'),
      criar: (dados) => requisitar('/substituicoes', { method: 'POST', body: JSON.stringify(dados) }),
      remover: (id) => requisitar(`/substituicoes/${id}`, { method: 'DELETE' }),
    },
    cep: {
      consultar: (cep) => requisitar(`/cep/${cep}`),
    },
    estatisticas: {
      obter: () => requisitar('/estatisticas'),
    },
  };
})();
/* Utilitários de acessibilidade: anúncios para leitores de tela e foco. */

const A11y = (() => {
  function anunciar(mensagem, tipo = 'polite') {
    const regiao = document.getElementById('regiao-anuncios');
    if (!regiao) return;
    regiao.setAttribute('aria-live', tipo);
    regiao.textContent = '';
    window.setTimeout(() => {
      regiao.textContent = mensagem;
    }, 100);
  }

  function focar(elemento) {
    if (!elemento) return;
    elemento.setAttribute('tabindex', '-1');
    elemento.focus();
  }

  function marcarErro(campoId, mensagem) {
    const campo = document.getElementById(campoId);
    if (!campo) return;
    campo.setAttribute('aria-invalid', 'true');
    campo.classList.add('is-invalid');

    const idErro = `${campoId}-erro`;
    let spanErro = document.getElementById(idErro);
    if (!spanErro) {
      spanErro = document.createElement('div');
      spanErro.id = idErro;
      spanErro.className = 'invalid-feedback';
      campo.parentNode.appendChild(spanErro);
    }
    spanErro.textContent = mensagem;
    campo.setAttribute('aria-describedby', idErro);
  }

  function limparErro(campoId) {
    const campo = document.getElementById(campoId);
    if (!campo) return;
    campo.removeAttribute('aria-invalid');
    campo.classList.remove('is-invalid');
    const spanErro = document.getElementById(`${campoId}-erro`);
    if (spanErro) spanErro.textContent = '';
  }

  function limparTodosErros(formulario) {
    formulario.querySelectorAll('[aria-invalid="true"]').forEach((campo) => {
      limparErro(campo.id);
    });
  }

  return { anunciar, focar, marcarErro, limparErro, limparTodosErros };
})();
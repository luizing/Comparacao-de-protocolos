const estado = { usuarios: [], musicas: [], playlists: [] };
const $ = (seletor) => document.querySelector(seletor);

function mensagem(texto, erro = false) {
  const elemento = $('#mensagem');
  elemento.textContent = texto;
  elemento.className = erro ? 'erro' : 'sucesso';
}

async function api(caminho, opcoes = {}) {
  const resposta = await fetch(`/api${caminho}`, {
    headers: { 'Content-Type': 'application/json', ...(opcoes.headers || {}) },
    ...opcoes
  });
  if (!resposta.ok) throw new Error((await resposta.text()) || `Erro ${resposta.status}`);
  return resposta.status === 204 ? null : resposta.json();
}

function botoes(tipo, item) {
  const relacao = tipo === 'usuario' ? `verPlaylistsUsuario(${item.id})`
    : tipo === 'musica' ? `verPlaylistsMusica(${item.id})` : `verMusicasPlaylist(${item.id})`;
  return `<div class="acoes"><button onclick="editar${tipo[0].toUpperCase() + tipo.slice(1)}(${item.id})">Editar</button>
    <button onclick="excluir('${tipo}s', ${item.id})">Excluir</button><button onclick="${relacao}">Relações</button></div>`;
}

function tabela(destino, cabecalhos, linhas) {
  $(destino).innerHTML = linhas.length ? `<table><thead><tr>${cabecalhos.map(c => `<th>${c}</th>`).join('')}</tr></thead><tbody>${linhas.join('')}</tbody></table>` : '<p>Nenhum registro encontrado.</p>';
}

async function carregarUsuarios() {
  try {
    estado.usuarios = await api('/usuarios');
    tabela('#usuarios', ['ID', 'Nome', 'Idade', 'Ações'], estado.usuarios.map(u => `<tr><td>${u.id}</td><td>${u.nome}</td><td>${u.idade}</td><td>${botoes('usuario', u)}</td></tr>`));
    opcoesPlaylist();
  } catch (e) { mensagem(e.message, true); }
}

async function carregarMusicas() {
  try {
    estado.musicas = await api('/musicas');
    tabela('#musicas', ['ID', 'Nome', 'Artista', 'Ações'], estado.musicas.map(m => `<tr><td>${m.id}</td><td>${m.nome}</td><td>${m.artista}</td><td>${botoes('musica', m)}</td></tr>`));
    opcoesPlaylist();
  } catch (e) { mensagem(e.message, true); }
}

async function carregarPlaylists() {
  try {
    estado.playlists = await api('/playlists');
    tabela('#playlists', ['ID', 'Nome', 'Usuário', 'Músicas', 'Ações'], estado.playlists.map(p => `<tr><td>${p.id}</td><td>${p.nome}</td><td>${p.usuarioId}</td><td>${p.musicaIds.join(', ') || '-'}</td><td>${botoes('playlist', p)}</td></tr>`));
  } catch (e) { mensagem(e.message, true); }
}

function opcoesPlaylist() {
  const usuarioAtual = $('#playlist-usuario').value;
  const musicasAtuais = [...$('#playlist-musicas').selectedOptions].map(o => o.value);
  $('#playlist-usuario').innerHTML = '<option value="">Selecione</option>' + estado.usuarios.map(u => `<option value="${u.id}">${u.nome} (#${u.id})</option>`).join('');
  $('#playlist-musicas').innerHTML = estado.musicas.map(m => `<option value="${m.id}">${m.nome} — ${m.artista}</option>`).join('');
  $('#playlist-usuario').value = usuarioAtual;
  [...$('#playlist-musicas').options].forEach(o => o.selected = musicasAtuais.includes(o.value));
}

function limparUsuario() { $('#form-usuario').reset(); $('#usuario-id').value = ''; }
function limparMusica() { $('#form-musica').reset(); $('#musica-id').value = ''; }
function limparPlaylist() { $('#form-playlist').reset(); $('#playlist-id').value = ''; }
function editarUsuario(id) { const u = estado.usuarios.find(x => x.id === id); $('#usuario-id').value = u.id; $('#usuario-nome').value = u.nome; $('#usuario-idade').value = u.idade; }
function editarMusica(id) { const m = estado.musicas.find(x => x.id === id); $('#musica-id').value = m.id; $('#musica-nome').value = m.nome; $('#musica-artista').value = m.artista; }
function editarPlaylist(id) { const p = estado.playlists.find(x => x.id === id); $('#playlist-id').value = p.id; $('#playlist-nome').value = p.nome; $('#playlist-usuario').value = p.usuarioId; [...$('#playlist-musicas').options].forEach(o => o.selected = p.musicaIds.includes(Number(o.value))); }

$('#form-usuario').addEventListener('submit', async e => {
  e.preventDefault(); const id = $('#usuario-id').value; const corpo = { nome: $('#usuario-nome').value, idade: Number($('#usuario-idade').value) };
  try { await api(`/usuarios${id ? `/${id}` : ''}`, { method: id ? 'PUT' : 'POST', body: JSON.stringify(corpo) }); limparUsuario(); await carregarUsuarios(); mensagem('Usuário salvo.'); } catch (erro) { mensagem(erro.message, true); }
});
$('#form-musica').addEventListener('submit', async e => {
  e.preventDefault(); const id = $('#musica-id').value; const corpo = { nome: $('#musica-nome').value, artista: $('#musica-artista').value };
  try { await api(`/musicas${id ? `/${id}` : ''}`, { method: id ? 'PUT' : 'POST', body: JSON.stringify(corpo) }); limparMusica(); await carregarMusicas(); mensagem('Música salva.'); } catch (erro) { mensagem(erro.message, true); }
});
$('#form-playlist').addEventListener('submit', async e => {
  e.preventDefault(); const id = $('#playlist-id').value; const corpo = { nome: $('#playlist-nome').value, usuarioId: Number($('#playlist-usuario').value), musicaIds: [...$('#playlist-musicas').selectedOptions].map(o => Number(o.value)) };
  try { await api(`/playlists${id ? `/${id}` : ''}`, { method: id ? 'PUT' : 'POST', body: JSON.stringify(corpo) }); limparPlaylist(); await carregarPlaylists(); mensagem('Playlist salva.'); } catch (erro) { mensagem(erro.message, true); }
});

async function excluir(tipo, id) {
  if (!confirm('Deseja excluir este registro?')) return;
  try { await api(`/${tipo}/${id}`, { method: 'DELETE' }); await carregarTudo(); mensagem('Registro excluído.'); } catch (e) { mensagem(e.message, true); }
}
async function verPlaylistsUsuario(id) { try { exibirRelacao(`Playlists do usuário #${id}`, await api(`/usuarios/${id}/playlists`)); } catch (e) { mensagem(e.message, true); } }
async function verPlaylistsMusica(id) { try { exibirRelacao(`Playlists da música #${id}`, await api(`/musicas/${id}/playlists`)); } catch (e) { mensagem(e.message, true); } }
async function verMusicasPlaylist(id) { try { exibirRelacao(`Músicas da playlist #${id}`, await api(`/playlists/${id}/musicas`)); } catch (e) { mensagem(e.message, true); } }
function exibirRelacao(titulo, itens) { alert(`${titulo}:\n${itens.length ? itens.map(i => JSON.stringify(i)).join('\n') : 'Nenhum registro.'}`); }
async function carregarTudo() { await Promise.all([carregarUsuarios(), carregarMusicas(), carregarPlaylists()]); }
carregarTudo();

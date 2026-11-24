const estado = { usuarios: [], musicas: [], playlists: [] };
const $ = (seletor) => document.querySelector(seletor);

function mensagem(texto, erro = false) {
  const elemento = $('#mensagem');
  elemento.textContent = texto;
  elemento.className = erro ? 'erro' : 'sucesso';
}

async function api(caminho, opcoes = {}) {
  const chamada = chamadaSoap(caminho, opcoes);
  const resposta = await fetch('/ws', {
    method: 'POST',
    headers: { 'Content-Type': 'text/xml; charset=utf-8' },
    body: envelopeSoap(chamada.operacao, chamada.corpo)
  });
  const xml = new DOMParser().parseFromString(await resposta.text(), 'text/xml');
  const falha = primeiroElemento(xml, 'Fault');
  if (!resposta.ok || falha) {
    throw new Error(texto(primeiroElemento(falha || xml, 'faultstring')) || texto(primeiroElemento(falha || xml, 'Text')) || `Erro SOAP ${resposta.status}`);
  }
  return respostaSoap(xml, chamada.operacao);
}

const namespaceSoap = 'http://example.com/demo/streaming';

function chamadaSoap(caminho, opcoes) {
  const metodo = opcoes.method || 'GET';
  const partes = caminho.split('/').filter(Boolean);
  const recurso = partes[0];
  const id = partes[1];
  const dados = opcoes.body ? JSON.parse(opcoes.body) : {};
  const nomes = { usuarios: 'Usuario', musicas: 'Musica', playlists: 'Playlist' };
  if (partes.length === 1 && metodo === 'GET') return { operacao: `Listar${recurso[0].toUpperCase() + recurso.slice(1)}`, corpo: '' };
  if (partes.length === 1 && metodo === 'POST') return { operacao: `Criar${nomes[recurso]}`, corpo: camposSoap(dados) };
  if (partes.length === 2 && metodo === 'GET') return { operacao: `Buscar${nomes[recurso]}`, corpo: tagSoap('id', id) };
  if (partes.length === 2 && metodo === 'PUT') return { operacao: `Atualizar${nomes[recurso]}`, corpo: tagSoap('id', id) + camposSoap(dados) };
  if (partes.length === 2 && metodo === 'DELETE') return { operacao: `Excluir${nomes[recurso]}`, corpo: tagSoap('id', id) };
  if (recurso === 'usuarios' && partes[2] === 'playlists') return { operacao: 'PlaylistsDoUsuario', corpo: tagSoap('id', id) };
  if (recurso === 'musicas' && partes[2] === 'playlists') return { operacao: 'PlaylistsDaMusica', corpo: tagSoap('id', id) };
  if (recurso === 'playlists' && partes[2] === 'musicas') return { operacao: 'MusicasDaPlaylist', corpo: tagSoap('id', id) };
  throw new Error('Operação SOAP não suportada.');
}

function envelopeSoap(operacao, corpo) {
  return `<?xml version="1.0" encoding="UTF-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:st="${namespaceSoap}">
      <soapenv:Body><st:${operacao}Request>${corpo}</st:${operacao}Request></soapenv:Body>
    </soapenv:Envelope>`;
}

function camposSoap(dados) {
  return Object.entries(dados).flatMap(([nome, valor]) => {
    if (nome === 'musicaIds') return valor.map(id => tagSoap('musicaId', id));
    return tagSoap(nome, valor);
  }).join('');
}

function tagSoap(nome, valor) { return `<st:${nome}>${escaparXml(valor)}</st:${nome}>`; }
function escaparXml(valor) { return String(valor).replace(/[<>&"']/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' })[c]); }
function primeiroElemento(no, nome) { return no && [...no.getElementsByTagNameNS('*', nome)][0]; }
function filhos(no, nome) { return [...no.children].filter(filho => filho.localName === nome); }
function texto(no) { return no ? no.textContent : ''; }

function respostaSoap(xml, operacao) {
  if (operacao.startsWith('Excluir')) return null;
  const resposta = primeiroElemento(xml, `${operacao}Response`);
  const tipo = operacao.includes('Usuario') ? 'usuario' : operacao.includes('Musica') ? 'musica' : 'playlist';
  const valores = filhos(resposta, tipo).map(elemento => objetoSoap(elemento, tipo));
  const lista = operacao.startsWith('Listar') || operacao.startsWith('Playlists') || operacao.startsWith('Musicas');
  return lista ? valores : valores[0];
}

function objetoSoap(elemento, tipo) {
  const valor = {};
  [...elemento.children].forEach(filho => {
    const nome = filho.localName;
    if (nome === 'musicaId') {
      valor.musicaIds = valor.musicaIds || [];
      valor.musicaIds.push(Number(texto(filho)));
    } else {
      valor[nome] = nome === 'id' || nome === 'idade' || nome === 'usuarioId' ? Number(texto(filho)) : texto(filho);
    }
  });
  if (tipo === 'playlist') valor.musicaIds = valor.musicaIds || [];
  return valor;
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

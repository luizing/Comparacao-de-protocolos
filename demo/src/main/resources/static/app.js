const estado = { usuarios: [], musicas: [], playlists: [] };
const $ = (seletor) => document.querySelector(seletor);

function mensagem(texto, erro = false) {
  const elemento = $('#mensagem');
  elemento.textContent = texto;
  elemento.className = erro ? 'erro' : 'sucesso';
}

async function api(caminho, opcoes = {}) {
  const chamada = chamadaGrpc(caminho, opcoes);
  const resposta = await fetch(`http://localhost:8081/catalogo.Catalogo/${chamada.operacao}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/grpc-web+proto',
      'X-Grpc-Web': '1',
      'X-User-Agent': 'catalogo-web'
    },
    body: frameGrpc(chamada.mensagem)
  });
  const bytes = new Uint8Array(await resposta.arrayBuffer());
  if (!resposta.ok) throw new Error(`Erro gRPC-Web ${resposta.status}`);
  return respostaGrpc(bytes, chamada.operacao);
}

function chamadaGrpc(caminho, opcoes) {
  const metodo = opcoes.method || 'GET';
  const partes = caminho.split('/').filter(Boolean);
  const recurso = partes[0];
  const id = partes[1];
  const dados = opcoes.body ? JSON.parse(opcoes.body) : {};
  const nomes = { usuarios: 'Usuario', musicas: 'Musica', playlists: 'Playlist' };
  if (partes.length === 1 && metodo === 'GET') return { operacao: `Listar${recurso[0].toUpperCase() + recurso.slice(1)}`, mensagem: new Uint8Array() };
  if (partes.length === 1 && metodo === 'POST') return { operacao: `Criar${nomes[recurso]}`, mensagem: mensagemRecurso(recurso, dados) };
  if (partes.length === 2 && metodo === 'GET') return { operacao: `Buscar${nomes[recurso]}`, mensagem: mensagemId(id) };
  if (partes.length === 2 && metodo === 'PUT') return { operacao: `Atualizar${nomes[recurso]}`, mensagem: mensagemAtualizacao(id, recurso, dados) };
  if (partes.length === 2 && metodo === 'DELETE') return { operacao: `Excluir${nomes[recurso]}`, mensagem: mensagemId(id) };
  if (recurso === 'usuarios' && partes[2] === 'playlists') return { operacao: 'ListarPlaylistsDoUsuario', mensagem: mensagemId(id) };
  if (recurso === 'musicas' && partes[2] === 'playlists') return { operacao: 'ListarPlaylistsDaMusica', mensagem: mensagemId(id) };
  if (recurso === 'playlists' && partes[2] === 'musicas') return { operacao: 'ListarMusicasDaPlaylist', mensagem: mensagemId(id) };
  throw new Error('Operação gRPC não suportada.');
}

function mensagemId(id) { return campoVarint(1, id); }
function mensagemAtualizacao(id, recurso, dados) { return juntar(campoVarint(1, id), campoBytes(2, mensagemRecurso(recurso, dados))); }
function mensagemRecurso(recurso, dados) {
  if (recurso === 'usuarios') return juntar(campoTexto(1, dados.nome), campoVarint(2, dados.idade));
  if (recurso === 'musicas') return juntar(campoTexto(1, dados.nome), campoTexto(2, dados.artista));
  return juntar(campoTexto(1, dados.nome), campoVarint(2, dados.usuarioId), ...(dados.musicaIds || []).map(id => campoVarint(3, id)));
}

function campoVarint(numero, valor) { return juntar(varint(numero << 3), varint(valor)); }
function campoTexto(numero, valor) { return campoBytes(numero, new TextEncoder().encode(valor)); }
function campoBytes(numero, valor) { return juntar(varint((numero << 3) | 2), varint(valor.length), valor); }
function varint(valor) {
  let numero = BigInt(valor);
  const bytes = [];
  do { let byte = Number(numero & 127n); numero >>= 7n; if (numero) byte |= 128; bytes.push(byte); } while (numero);
  return new Uint8Array(bytes);
}
function juntar(...partes) {
  const tamanho = partes.reduce((total, parte) => total + parte.length, 0);
  const resultado = new Uint8Array(tamanho); let posicao = 0;
  partes.forEach(parte => { resultado.set(parte, posicao); posicao += parte.length; });
  return resultado;
}
function frameGrpc(mensagem) {
  const frame = new Uint8Array(mensagem.length + 5);
  new DataView(frame.buffer).setUint32(1, mensagem.length, false);
  frame.set(mensagem, 5);
  return frame;
}

function respostaGrpc(bytes, operacao) {
  let posicao = 0; let mensagem;
  while (posicao < bytes.length) {
    const marcador = bytes[posicao++];
    const tamanho = new DataView(bytes.buffer, bytes.byteOffset + posicao, 4).getUint32(0, false); posicao += 4;
    const frame = bytes.slice(posicao, posicao + tamanho); posicao += tamanho;
    if (marcador & 128) {
      const trailers = new TextDecoder().decode(frame);
      const status = /grpc-status: *(\d+)/i.exec(trailers);
      if (status && status[1] !== '0') throw new Error(decodeURIComponent((/grpc-message: *([^\r\n]*)/i.exec(trailers) || [, 'Erro gRPC'])[1]));
    } else mensagem = frame;
  }
  if (operacao.startsWith('Excluir')) return null;
  if (!mensagem) throw new Error('Resposta gRPC vazia.');
  const tipo = operacao.includes('Usuario') ? 'usuario' : operacao.includes('Musica') ? 'musica' : 'playlist';
  const lista = operacao.startsWith('Listar');
  return lista ? camposProtobuf(mensagem, 1).map(valor => objetoGrpc(valor, tipo)) : objetoGrpc(mensagem, tipo);
}

function objetoGrpc(bytes, tipo) {
  const campos = lerCampos(bytes);
  const numero = indice => Number(campos.get(indice)?.[0] || 0n);
  const texto = indice => new TextDecoder().decode(campos.get(indice)?.[0] || new Uint8Array());
  if (tipo === 'usuario') return { id: numero(1), nome: texto(2), idade: numero(3) };
  if (tipo === 'musica') return { id: numero(1), nome: texto(2), artista: texto(3) };
  return { id: numero(1), nome: texto(2), usuarioId: numero(3), musicaIds: camposProtobuf(bytes, 4).map(Number) };
}

function camposProtobuf(bytes, indice) { return lerCampos(bytes).get(indice) || []; }
function lerCampos(bytes) {
  const campos = new Map(); let posicao = 0;
  while (posicao < bytes.length) {
    const [chave, proxima] = lerVarint(bytes, posicao); posicao = proxima;
    const indice = Number(chave >> 3n); const wire = Number(chave & 7n); let valor;
    if (wire === 0) [valor, posicao] = lerVarint(bytes, posicao);
    else if (wire === 2) { const [tamanho, inicio] = lerVarint(bytes, posicao); posicao = inicio; valor = bytes.slice(posicao, posicao + Number(tamanho)); posicao += Number(tamanho); }
    else throw new Error('Campo Protobuf não suportado.');
    campos.set(indice, [...(campos.get(indice) || []), valor]);
  }
  return campos;
}
function lerVarint(bytes, posicao) {
  let valor = 0n; let deslocamento = 0n;
  while (true) { const byte = BigInt(bytes[posicao++]); valor |= (byte & 127n) << deslocamento; if (!(byte & 128n)) return [valor, posicao]; deslocamento += 7n; }
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

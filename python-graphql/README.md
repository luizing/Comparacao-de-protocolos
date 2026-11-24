# Streaming de Músicas: GraphQL em Python

Versão GraphQL do serviço em Python, feita com Strawberry e FastAPI. Os dados ficam num banco SQLite em memória.

## Como rodar

```bash
cd python-graphql
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python main.py
```

Abra `http://localhost:8000/graphql`. O GraphiQL, editor que roda no navegador, permite executar as consultas abaixo.

## Exemplos

```graphql
mutation { criarUsuario(input: {nome: "Ana", idade: 20}) { id nome idade } }
mutation { criarMusica(input: {nome: "Song A", artista: "X"}) { id } }
mutation { criarPlaylist(input: {nome: "Fav", usuarioId: 1, musicaIds: [1]}) { id musicaIds } }
mutation { atualizarUsuario(id: 1, input: {nome: "Ana B", idade: 21}) { nome } }
mutation { excluirMusica(id: 1) }

{ usuarios { id nome idade } }
{ musicas { id nome artista } }
{ playlistsDoUsuario(usuarioId: 1) { nome } }
{ musicasDaPlaylist(playlistId: 1) { nome artista } }
{ playlistsDaMusica(musicaId: 1) { nome } }

# Consulta aninhada: os dados relacionados vêm numa requisição só
{ usuario(id: 1) { nome playlists { nome musicas { nome artista } } } }
```

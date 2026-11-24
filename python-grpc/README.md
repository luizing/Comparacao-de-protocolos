# Streaming de Músicas: gRPC em Python

Versão gRPC do serviço em Python, feita com grpcio. O contrato do serviço fica em `streaming.proto`.
Os dados ficam num banco SQLite em memória.

## Como rodar

```bash
cd python-grpc
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python server.py              # sobe na porta 50051
```

Em outro terminal, também com o `.venv` ativado:

```bash
python client.py              # executa o CRUD completo e as 3 consultas
```

Os arquivos `streaming_pb2.py` e `streaming_pb2_grpc.py` já estão no repositório. Se você alterar o `.proto`, gere os dois de novo com:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. streaming.proto
```

## Operações

`ListarUsuarios`, `BuscarUsuario`, `CriarUsuario`, `AtualizarUsuario`, `ExcluirUsuario`. As mesmas existem para Músicas e Playlists.

Consultas do enunciado: `PlaylistsDoUsuario`, `MusicasDaPlaylist`, `PlaylistsDaMusica`.

Quando o id não existe, o servidor responde com o status `NOT_FOUND`, que equivale ao 404 do REST.

# Streaming de Músicas: gRPC em Python

Versão gRPC do serviço em Python, feita com grpcio.
**O contrato é o mesmo da versão Java:** o `catalogo.proto` é cópia do arquivo da branch `grpc`. Um cliente feito para uma versão funciona com a outra. Por exemplo, `python client.py localhost:9090` roda o cliente Python contra o servidor Java.
Os dados ficam num banco SQLite em memória.

## Como rodar

```bash
cd python-grpc
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python server.py              # sobe na porta 50051 (outra porta: python server.py 50052)
```

Em outro terminal, também com o `.venv` ativado:

```bash
python client.py              # executa o CRUD completo e as 3 consultas
```

Os arquivos `catalogo_pb2.py` e `catalogo_pb2_grpc.py` já estão no repositório. Se você alterar o `.proto`, gere os dois de novo com:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. catalogo.proto
```

## Operações

`ListarUsuarios`, `BuscarUsuario`, `CriarUsuario`, `AtualizarUsuario`, `ExcluirUsuario`. As mesmas existem para Músicas e Playlists.

Consultas do enunciado: `ListarPlaylistsDoUsuario`, `ListarMusicasDaPlaylist`, `ListarPlaylistsDaMusica`.

Quando o id não existe, o servidor responde com o status `NOT_FOUND`, que equivale ao 404 do REST.

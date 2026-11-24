# Streaming de Músicas: REST em Python

Versão em Python (FastAPI) do serviço REST, com os mesmos endpoints e campos da versão Java em `demo/`.
Os dados ficam num banco SQLite em memória, como o H2 da versão Java.

## Como rodar

```bash
cd python-rest
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python main.py
```

O serviço sobe em `http://localhost:8080`. A documentação interativa (Swagger) fica em `http://localhost:8080/docs`, e dá para testar todo o CRUD por ela.

## Endpoints

| Recurso   | Operações                                                    | Consulta extra                     |
|-----------|--------------------------------------------------------------|------------------------------------|
| Usuários  | `GET/POST /api/usuarios`, `GET/PUT/DELETE /api/usuarios/{id}`   | `GET /api/usuarios/{id}/playlists` |
| Músicas   | `GET/POST /api/musicas`, `GET/PUT/DELETE /api/musicas/{id}`     | `GET /api/musicas/{id}/playlists`  |
| Playlists | `GET/POST /api/playlists`, `GET/PUT/DELETE /api/playlists/{id}` | `GET /api/playlists/{id}/musicas`  |

Exemplos de corpo:
- `POST /api/usuarios`: `{"nome": "Ana", "idade": 20}`
- `POST /api/musicas`: `{"nome": "Song A", "artista": "X"}`
- `POST /api/playlists`: `{"nome": "Favoritas", "usuarioId": 1, "musicaIds": [1, 2]}`

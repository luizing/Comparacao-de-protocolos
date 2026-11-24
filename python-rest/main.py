"""Serviço de streaming de músicas - versão REST em Python (FastAPI).

Mesmos endpoints da versão Java (Spring Boot):
  /api/usuarios, /api/musicas, /api/playlists
"""
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from catalogo import Catalogo, NaoEncontrado

app = FastAPI(title="Streaming de Músicas - REST (Python)")
service = Catalogo()


@app.exception_handler(NaoEncontrado)
async def nao_encontrado(_: Request, exc: NaoEncontrado):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


# ---------- DTOs ----------
class UsuarioRequest(BaseModel):
    nome: str
    idade: Optional[int] = None


class UsuarioResponse(UsuarioRequest):
    id: int


class MusicaRequest(BaseModel):
    nome: str
    artista: Optional[str] = None


class MusicaResponse(MusicaRequest):
    id: int


class PlaylistRequest(BaseModel):
    nome: str
    usuarioId: int
    musicaIds: List[int] = []


class PlaylistResponse(PlaylistRequest):
    id: int


# ---------- usuários ----------
@app.get("/api/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios():
    return service.listar_usuarios()


@app.get("/api/usuarios/{id}", response_model=UsuarioResponse)
def buscar_usuario(id: int):
    return service.buscar_usuario(id)


@app.post("/api/usuarios", response_model=UsuarioResponse, status_code=201)
def criar_usuario(req: UsuarioRequest):
    return service.criar_usuario(req.nome, req.idade)


@app.put("/api/usuarios/{id}", response_model=UsuarioResponse)
def atualizar_usuario(id: int, req: UsuarioRequest):
    return service.atualizar_usuario(id, req.nome, req.idade)


@app.delete("/api/usuarios/{id}", status_code=204)
def excluir_usuario(id: int):
    service.excluir_usuario(id)
    return Response(status_code=204)


@app.get("/api/usuarios/{id}/playlists", response_model=List[PlaylistResponse])
def playlists_do_usuario(id: int):
    return service.playlists_do_usuario(id)


# ---------- músicas ----------
@app.get("/api/musicas", response_model=List[MusicaResponse])
def listar_musicas():
    return service.listar_musicas()


@app.get("/api/musicas/{id}", response_model=MusicaResponse)
def buscar_musica(id: int):
    return service.buscar_musica(id)


@app.post("/api/musicas", response_model=MusicaResponse, status_code=201)
def criar_musica(req: MusicaRequest):
    return service.criar_musica(req.nome, req.artista)


@app.put("/api/musicas/{id}", response_model=MusicaResponse)
def atualizar_musica(id: int, req: MusicaRequest):
    return service.atualizar_musica(id, req.nome, req.artista)


@app.delete("/api/musicas/{id}", status_code=204)
def excluir_musica(id: int):
    service.excluir_musica(id)
    return Response(status_code=204)


@app.get("/api/musicas/{id}/playlists", response_model=List[PlaylistResponse])
def playlists_da_musica(id: int):
    return service.playlists_da_musica(id)


# ---------- playlists ----------
@app.get("/api/playlists", response_model=List[PlaylistResponse])
def listar_playlists():
    return service.listar_playlists()


@app.get("/api/playlists/{id}", response_model=PlaylistResponse)
def buscar_playlist(id: int):
    return service.buscar_playlist(id)


@app.post("/api/playlists", response_model=PlaylistResponse, status_code=201)
def criar_playlist(req: PlaylistRequest):
    return service.criar_playlist(req.nome, req.usuarioId, req.musicaIds)


@app.put("/api/playlists/{id}", response_model=PlaylistResponse)
def atualizar_playlist(id: int, req: PlaylistRequest):
    return service.atualizar_playlist(id, req.nome, req.usuarioId, req.musicaIds)


@app.delete("/api/playlists/{id}", status_code=204)
def excluir_playlist(id: int):
    service.excluir_playlist(id)
    return Response(status_code=204)


@app.get("/api/playlists/{id}/musicas", response_model=List[MusicaResponse])
def musicas_da_playlist(id: int):
    return service.musicas_da_playlist(id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

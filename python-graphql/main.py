"""Serviço de streaming de músicas - versão GraphQL em Python (Strawberry + FastAPI).

Endpoint único: POST /graphql (GraphiQL em http://localhost:8000/graphql)
"""
from typing import List, Optional

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from catalogo import Catalogo

service = Catalogo()


# ---------- tipos ----------
@strawberry.type
class Usuario:
    id: strawberry.ID
    nome: str
    idade: Optional[int]

    @strawberry.field
    def playlists(self) -> List["Playlist"]:
        return [playlist(p) for p in service.playlists_do_usuario(int(self.id))]


@strawberry.type
class Musica:
    id: strawberry.ID
    nome: str
    artista: Optional[str]

    @strawberry.field
    def playlists(self) -> List["Playlist"]:
        return [playlist(p) for p in service.playlists_da_musica(int(self.id))]


@strawberry.type
class Playlist:
    id: strawberry.ID
    nome: str
    usuario_id: strawberry.ID
    musica_ids: List[strawberry.ID]

    @strawberry.field
    def usuario(self) -> Usuario:
        return usuario(service.buscar_usuario(int(self.usuario_id)))

    @strawberry.field
    def musicas(self) -> List[Musica]:
        return [musica(m) for m in service.musicas_da_playlist(int(self.id))]


def usuario(d) -> Usuario:
    return Usuario(id=d["id"], nome=d["nome"], idade=d["idade"])


def musica(d) -> Musica:
    return Musica(id=d["id"], nome=d["nome"], artista=d["artista"])


def playlist(d) -> Playlist:
    return Playlist(id=d["id"], nome=d["nome"], usuario_id=d["usuarioId"], musica_ids=d["musicaIds"])


# ---------- inputs ----------
@strawberry.input
class UsuarioInput:
    nome: str
    idade: Optional[int] = None


@strawberry.input
class MusicaInput:
    nome: str
    artista: Optional[str] = None


@strawberry.input
class PlaylistInput:
    nome: str
    usuario_id: strawberry.ID
    musica_ids: List[strawberry.ID] = strawberry.field(default_factory=list)


# ---------- consultas ----------
@strawberry.type
class Query:
    @strawberry.field
    def usuarios(self) -> List[Usuario]:
        return [usuario(u) for u in service.listar_usuarios()]

    @strawberry.field
    def usuario(self, id: strawberry.ID) -> Usuario:
        return usuario(service.buscar_usuario(int(id)))

    @strawberry.field
    def musicas(self) -> List[Musica]:
        return [musica(m) for m in service.listar_musicas()]

    @strawberry.field
    def musica(self, id: strawberry.ID) -> Musica:
        return musica(service.buscar_musica(int(id)))

    @strawberry.field
    def playlists(self) -> List[Playlist]:
        return [playlist(p) for p in service.listar_playlists()]

    @strawberry.field
    def playlist(self, id: strawberry.ID) -> Playlist:
        return playlist(service.buscar_playlist(int(id)))

    # consultas pedidas no enunciado (também acessíveis pelos campos aninhados)
    @strawberry.field
    def playlists_do_usuario(self, usuario_id: strawberry.ID) -> List[Playlist]:
        return [playlist(p) for p in service.playlists_do_usuario(int(usuario_id))]

    @strawberry.field
    def musicas_da_playlist(self, playlist_id: strawberry.ID) -> List[Musica]:
        return [musica(m) for m in service.musicas_da_playlist(int(playlist_id))]

    @strawberry.field
    def playlists_da_musica(self, musica_id: strawberry.ID) -> List[Playlist]:
        return [playlist(p) for p in service.playlists_da_musica(int(musica_id))]


# ---------- alterações ----------
def _ids(ids):
    return [int(i) for i in ids]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def criar_usuario(self, input: UsuarioInput) -> Usuario:
        return usuario(service.criar_usuario(input.nome, input.idade))

    @strawberry.mutation
    def atualizar_usuario(self, id: strawberry.ID, input: UsuarioInput) -> Usuario:
        return usuario(service.atualizar_usuario(int(id), input.nome, input.idade))

    @strawberry.mutation
    def excluir_usuario(self, id: strawberry.ID) -> bool:
        service.excluir_usuario(int(id))
        return True

    @strawberry.mutation
    def criar_musica(self, input: MusicaInput) -> Musica:
        return musica(service.criar_musica(input.nome, input.artista))

    @strawberry.mutation
    def atualizar_musica(self, id: strawberry.ID, input: MusicaInput) -> Musica:
        return musica(service.atualizar_musica(int(id), input.nome, input.artista))

    @strawberry.mutation
    def excluir_musica(self, id: strawberry.ID) -> bool:
        service.excluir_musica(int(id))
        return True

    @strawberry.mutation
    def criar_playlist(self, input: PlaylistInput) -> Playlist:
        return playlist(service.criar_playlist(input.nome, int(input.usuario_id), _ids(input.musica_ids)))

    @strawberry.mutation
    def atualizar_playlist(self, id: strawberry.ID, input: PlaylistInput) -> Playlist:
        return playlist(service.atualizar_playlist(int(id), input.nome, int(input.usuario_id), _ids(input.musica_ids)))

    @strawberry.mutation
    def excluir_playlist(self, id: strawberry.ID) -> bool:
        service.excluir_playlist(int(id))
        return True


schema = strawberry.Schema(query=Query, mutation=Mutation)
app = FastAPI(title="Streaming de Músicas - GraphQL (Python)")
app.include_router(GraphQLRouter(schema), prefix="/graphql")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

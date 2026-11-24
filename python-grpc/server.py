"""Serviço de streaming de músicas - versão gRPC em Python (grpcio).

Usa o MESMO contrato da versão Java (catalogo.proto, branch grpc), então
qualquer cliente funciona com as duas versões.

Se alterar o .proto, gere o código de novo:
  python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. catalogo.proto
"""
import sys
from concurrent import futures

import grpc
from google.protobuf import empty_pb2

import catalogo_pb2 as pb
import catalogo_pb2_grpc as pb_grpc
from catalogo import Catalogo, NaoEncontrado

VAZIO = empty_pb2.Empty()


def usuario(d):
    return pb.Usuario(id=d["id"], nome=d["nome"], idade=d["idade"] or 0)


def musica(d):
    return pb.Musica(id=d["id"], nome=d["nome"], artista=d["artista"] or "")


def playlist(d):
    return pb.Playlist(id=d["id"], nome=d["nome"], usuario_id=d["usuarioId"], musica_ids=d["musicaIds"])


def trata_erros(metodo):
    """Converte NaoEncontrado em status NOT_FOUND do gRPC (equivalente ao 404 do REST)."""
    def wrapper(self, request, context):
        try:
            return metodo(self, request, context)
        except NaoEncontrado as e:
            context.abort(grpc.StatusCode.NOT_FOUND, str(e))
    return wrapper


class CatalogoService(pb_grpc.CatalogoServicer):
    def __init__(self):
        self.s = Catalogo()

    # ---------- usuários ----------
    @trata_erros
    def ListarUsuarios(self, req, ctx):
        return pb.UsuariosResponse(usuarios=[usuario(u) for u in self.s.listar_usuarios()])

    @trata_erros
    def BuscarUsuario(self, req, ctx):
        return usuario(self.s.buscar_usuario(req.id))

    @trata_erros
    def CriarUsuario(self, req, ctx):
        return usuario(self.s.criar_usuario(req.nome, req.idade))

    @trata_erros
    def AtualizarUsuario(self, req, ctx):
        return usuario(self.s.atualizar_usuario(req.id, req.input.nome, req.input.idade))

    @trata_erros
    def ExcluirUsuario(self, req, ctx):
        self.s.excluir_usuario(req.id)
        return VAZIO

    # ---------- músicas ----------
    @trata_erros
    def ListarMusicas(self, req, ctx):
        return pb.MusicasResponse(musicas=[musica(m) for m in self.s.listar_musicas()])

    @trata_erros
    def BuscarMusica(self, req, ctx):
        return musica(self.s.buscar_musica(req.id))

    @trata_erros
    def CriarMusica(self, req, ctx):
        return musica(self.s.criar_musica(req.nome, req.artista))

    @trata_erros
    def AtualizarMusica(self, req, ctx):
        return musica(self.s.atualizar_musica(req.id, req.input.nome, req.input.artista))

    @trata_erros
    def ExcluirMusica(self, req, ctx):
        self.s.excluir_musica(req.id)
        return VAZIO

    # ---------- playlists ----------
    @trata_erros
    def ListarPlaylists(self, req, ctx):
        return pb.PlaylistsResponse(playlists=[playlist(p) for p in self.s.listar_playlists()])

    @trata_erros
    def BuscarPlaylist(self, req, ctx):
        return playlist(self.s.buscar_playlist(req.id))

    @trata_erros
    def CriarPlaylist(self, req, ctx):
        return playlist(self.s.criar_playlist(req.nome, req.usuario_id, list(req.musica_ids)))

    @trata_erros
    def AtualizarPlaylist(self, req, ctx):
        i = req.input
        return playlist(self.s.atualizar_playlist(req.id, i.nome, i.usuario_id, list(i.musica_ids)))

    @trata_erros
    def ExcluirPlaylist(self, req, ctx):
        self.s.excluir_playlist(req.id)
        return VAZIO

    # ---------- consultas ----------
    @trata_erros
    def ListarPlaylistsDoUsuario(self, req, ctx):
        return pb.PlaylistsResponse(playlists=[playlist(p) for p in self.s.playlists_do_usuario(req.id)])

    @trata_erros
    def ListarMusicasDaPlaylist(self, req, ctx):
        return pb.MusicasResponse(musicas=[musica(m) for m in self.s.musicas_da_playlist(req.id)])

    @trata_erros
    def ListarPlaylistsDaMusica(self, req, ctx):
        return pb.PlaylistsResponse(playlists=[playlist(p) for p in self.s.playlists_da_musica(req.id)])


def serve(porta=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_CatalogoServicer_to_server(CatalogoService(), server)
    server.add_insecure_port(f"[::]:{porta}")
    server.start()
    print(f"Servidor gRPC rodando na porta {porta}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve(int(sys.argv[1]) if len(sys.argv) > 1 else 50051)

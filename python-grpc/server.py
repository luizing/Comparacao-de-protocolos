"""Serviço de streaming de músicas - versão gRPC em Python (grpcio).

Gere o código a partir do .proto antes de rodar:
  python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. streaming.proto
"""
from concurrent import futures

import grpc

import streaming_pb2 as pb
import streaming_pb2_grpc as pb_grpc
from catalogo import Catalogo, NaoEncontrado


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


class StreamingService(pb_grpc.StreamingServicer):
    def __init__(self):
        self.s = Catalogo()

    # ---------- usuários ----------
    @trata_erros
    def ListarUsuarios(self, req, ctx):
        return pb.ListaUsuarios(usuarios=[usuario(u) for u in self.s.listar_usuarios()])

    @trata_erros
    def BuscarUsuario(self, req, ctx):
        return usuario(self.s.buscar_usuario(req.id))

    @trata_erros
    def CriarUsuario(self, req, ctx):
        return usuario(self.s.criar_usuario(req.nome, req.idade))

    @trata_erros
    def AtualizarUsuario(self, req, ctx):
        return usuario(self.s.atualizar_usuario(req.id, req.nome, req.idade))

    @trata_erros
    def ExcluirUsuario(self, req, ctx):
        self.s.excluir_usuario(req.id)
        return pb.Vazio()

    # ---------- músicas ----------
    @trata_erros
    def ListarMusicas(self, req, ctx):
        return pb.ListaMusicas(musicas=[musica(m) for m in self.s.listar_musicas()])

    @trata_erros
    def BuscarMusica(self, req, ctx):
        return musica(self.s.buscar_musica(req.id))

    @trata_erros
    def CriarMusica(self, req, ctx):
        return musica(self.s.criar_musica(req.nome, req.artista))

    @trata_erros
    def AtualizarMusica(self, req, ctx):
        return musica(self.s.atualizar_musica(req.id, req.nome, req.artista))

    @trata_erros
    def ExcluirMusica(self, req, ctx):
        self.s.excluir_musica(req.id)
        return pb.Vazio()

    # ---------- playlists ----------
    @trata_erros
    def ListarPlaylists(self, req, ctx):
        return pb.ListaPlaylists(playlists=[playlist(p) for p in self.s.listar_playlists()])

    @trata_erros
    def BuscarPlaylist(self, req, ctx):
        return playlist(self.s.buscar_playlist(req.id))

    @trata_erros
    def CriarPlaylist(self, req, ctx):
        return playlist(self.s.criar_playlist(req.nome, req.usuario_id, list(req.musica_ids)))

    @trata_erros
    def AtualizarPlaylist(self, req, ctx):
        return playlist(self.s.atualizar_playlist(req.id, req.nome, req.usuario_id, list(req.musica_ids)))

    @trata_erros
    def ExcluirPlaylist(self, req, ctx):
        self.s.excluir_playlist(req.id)
        return pb.Vazio()

    # ---------- consultas ----------
    @trata_erros
    def PlaylistsDoUsuario(self, req, ctx):
        return pb.ListaPlaylists(playlists=[playlist(p) for p in self.s.playlists_do_usuario(req.id)])

    @trata_erros
    def MusicasDaPlaylist(self, req, ctx):
        return pb.ListaMusicas(musicas=[musica(m) for m in self.s.musicas_da_playlist(req.id)])

    @trata_erros
    def PlaylistsDaMusica(self, req, ctx):
        return pb.ListaPlaylists(playlists=[playlist(p) for p in self.s.playlists_da_musica(req.id)])


def serve(porta=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_StreamingServicer_to_server(StreamingService(), server)
    server.add_insecure_port(f"[::]:{porta}")
    server.start()
    print(f"Servidor gRPC rodando na porta {porta}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

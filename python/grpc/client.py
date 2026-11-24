"""Cliente de demonstração: executa o CRUD completo no servidor gRPC.

Rode primeiro o server.py em outro terminal. Como o contrato é o mesmo,
o cliente também funciona com a versão Java: python client.py localhost:9090
"""
import sys

import grpc
from google.protobuf import empty_pb2

import catalogo_pb2 as pb
import catalogo_pb2_grpc as pb_grpc

VAZIO = empty_pb2.Empty()


def main(endereco="localhost:50051"):
    with grpc.insecure_channel(endereco) as canal:
        s = pb_grpc.CatalogoStub(canal)

        ana = s.CriarUsuario(pb.UsuarioRequest(nome="Ana", idade=20))
        m1 = s.CriarMusica(pb.MusicaRequest(nome="Song A", artista="X"))
        m2 = s.CriarMusica(pb.MusicaRequest(nome="Song B", artista="Y"))
        fav = s.CriarPlaylist(pb.PlaylistRequest(nome="Fav", usuario_id=ana.id, musica_ids=[m1.id, m2.id]))
        print("Playlist criada:", fav)

        print("Usuários:", s.ListarUsuarios(VAZIO))
        print("Músicas:", s.ListarMusicas(VAZIO))
        print("Playlists do usuário:", s.ListarPlaylistsDoUsuario(pb.IdRequest(id=ana.id)))
        print("Músicas da playlist:", s.ListarMusicasDaPlaylist(pb.IdRequest(id=fav.id)))
        print("Playlists da música:", s.ListarPlaylistsDaMusica(pb.IdRequest(id=m1.id)))

        print("Atualizado:", s.AtualizarUsuario(pb.AtualizarUsuarioRequest(
            id=ana.id, input=pb.UsuarioRequest(nome="Ana B", idade=21))))
        s.ExcluirMusica(pb.IdRequest(id=m1.id))
        print("Playlist após excluir música:", s.BuscarPlaylist(pb.IdRequest(id=fav.id)))

        try:
            s.BuscarUsuario(pb.IdRequest(id=99))
        except grpc.RpcError as e:
            print("Erro esperado:", e.code(), e.details())

        s.ExcluirUsuario(pb.IdRequest(id=ana.id))
        print("Playlists após excluir usuário:", s.ListarPlaylists(VAZIO))


if __name__ == "__main__":
    main(*sys.argv[1:])

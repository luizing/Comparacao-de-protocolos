"""Cliente de demonstração: executa o CRUD completo no servidor gRPC.

Rode primeiro o server.py em outro terminal.
"""
import grpc

import streaming_pb2 as pb
import streaming_pb2_grpc as pb_grpc


def main():
    with grpc.insecure_channel("localhost:50051") as canal:
        s = pb_grpc.StreamingStub(canal)

        ana = s.CriarUsuario(pb.UsuarioRequest(nome="Ana", idade=20))
        m1 = s.CriarMusica(pb.MusicaRequest(nome="Song A", artista="X"))
        m2 = s.CriarMusica(pb.MusicaRequest(nome="Song B", artista="Y"))
        fav = s.CriarPlaylist(pb.PlaylistRequest(nome="Fav", usuario_id=ana.id, musica_ids=[m1.id, m2.id]))
        print("Playlist criada:", fav)

        print("Usuários:", s.ListarUsuarios(pb.Vazio()))
        print("Músicas:", s.ListarMusicas(pb.Vazio()))
        print("Playlists do usuário:", s.PlaylistsDoUsuario(pb.Id(id=ana.id)))
        print("Músicas da playlist:", s.MusicasDaPlaylist(pb.Id(id=fav.id)))
        print("Playlists da música:", s.PlaylistsDaMusica(pb.Id(id=m1.id)))

        print("Atualizado:", s.AtualizarUsuario(pb.AtualizarUsuarioRequest(id=ana.id, nome="Ana B", idade=21)))
        s.ExcluirMusica(pb.Id(id=m1.id))
        print("Playlist após excluir música:", s.BuscarPlaylist(pb.Id(id=fav.id)))

        try:
            s.BuscarUsuario(pb.Id(id=99))
        except grpc.RpcError as e:
            print("Erro esperado:", e.code(), e.details())

        s.ExcluirUsuario(pb.Id(id=ana.id))
        print("Playlists após excluir usuário:", s.ListarPlaylists(pb.Vazio()))


if __name__ == "__main__":
    main()

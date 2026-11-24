"""Cliente de demonstração com zeep, uma biblioteca padrão de cliente SOAP.

Ele lê o WSDL e executa o CRUD completo. Rode primeiro o main.py em outro terminal.
"""
from zeep import Client
from zeep.exceptions import Fault


def main():
    s = Client("http://localhost:8003/ws/streaming.wsdl").service

    ana = s.CriarUsuario(nome="Ana", idade=20)
    m1 = s.CriarMusica(nome="Song A", artista="X")
    m2 = s.CriarMusica(nome="Song B", artista="Y")
    fav = s.CriarPlaylist(nome="Fav", usuarioId=ana.id, musicaId=[m1.id, m2.id])
    print("Playlist criada:", fav)

    print("Usuários:", s.ListarUsuarios())
    print("Músicas:", s.ListarMusicas())
    print("Playlists do usuário:", s.PlaylistsDoUsuario(id=ana.id))
    print("Músicas da playlist:", s.MusicasDaPlaylist(id=fav.id))
    print("Playlists da música:", s.PlaylistsDaMusica(id=m1.id))

    print("Atualizado:", s.AtualizarUsuario(id=ana.id, nome="Ana B", idade=21))
    s.ExcluirMusica(id=m1.id)
    print("Playlist após excluir música:", s.BuscarPlaylist(id=fav.id))

    try:
        s.BuscarUsuario(id=99)
    except Fault as e:
        print("Erro esperado (SOAP Fault):", e.message)

    s.ExcluirUsuario(id=ana.id)
    print("Playlists após excluir usuário:", s.ListarPlaylists())


if __name__ == "__main__":
    main()

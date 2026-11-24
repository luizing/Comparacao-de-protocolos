package com.example.demo.grpc;

import com.example.demo.dto.MusicaResponse;
import com.example.demo.dto.PlaylistResponse;
import com.example.demo.dto.UsuarioResponse;
import com.example.demo.service.CatalogoService;
import com.google.protobuf.Empty;
import io.grpc.Status;
import io.grpc.stub.StreamObserver;
import java.util.NoSuchElementException;
import java.util.function.Supplier;
import org.springframework.stereotype.Service;

/** Implementação gRPC que delega as regras de negócio ao catálogo existente. */
@Service
public class CatalogoGrpcService extends CatalogoGrpc.CatalogoImplBase {

    private final CatalogoService service;

    public CatalogoGrpcService(CatalogoService service) {
        this.service = service;
    }

    @Override
    public void listarUsuarios(Empty request, StreamObserver<UsuariosResponse> responseObserver) {
        responder(responseObserver, () -> UsuariosResponse.newBuilder()
                .addAllUsuarios(service.listarUsuarios().stream().map(this::usuario).toList()).build());
    }

    @Override
    public void buscarUsuario(IdRequest request, StreamObserver<Usuario> responseObserver) {
        responder(responseObserver, () -> usuario(service.buscarUsuario(request.getId())));
    }

    @Override
    public void criarUsuario(UsuarioRequest request, StreamObserver<Usuario> responseObserver) {
        responder(responseObserver, () -> usuario(service.criarUsuario(new com.example.demo.dto.UsuarioRequest(request.getNome(), request.getIdade()))));
    }

    @Override
    public void atualizarUsuario(AtualizarUsuarioRequest request, StreamObserver<Usuario> responseObserver) {
        responder(responseObserver, () -> usuario(service.atualizarUsuario(request.getId(), new com.example.demo.dto.UsuarioRequest(request.getInput().getNome(), request.getInput().getIdade()))));
    }

    @Override
    public void excluirUsuario(IdRequest request, StreamObserver<Empty> responseObserver) {
        responder(responseObserver, () -> { service.excluirUsuario(request.getId()); return Empty.getDefaultInstance(); });
    }

    @Override
    public void listarMusicas(Empty request, StreamObserver<MusicasResponse> responseObserver) {
        responder(responseObserver, () -> MusicasResponse.newBuilder()
                .addAllMusicas(service.listarMusicas().stream().map(this::musica).toList()).build());
    }

    @Override
    public void buscarMusica(IdRequest request, StreamObserver<Musica> responseObserver) {
        responder(responseObserver, () -> musica(service.buscarMusica(request.getId())));
    }

    @Override
    public void criarMusica(MusicaRequest request, StreamObserver<Musica> responseObserver) {
        responder(responseObserver, () -> musica(service.criarMusica(new com.example.demo.dto.MusicaRequest(request.getNome(), request.getArtista()))));
    }

    @Override
    public void atualizarMusica(AtualizarMusicaRequest request, StreamObserver<Musica> responseObserver) {
        responder(responseObserver, () -> musica(service.atualizarMusica(request.getId(), new com.example.demo.dto.MusicaRequest(request.getInput().getNome(), request.getInput().getArtista()))));
    }

    @Override
    public void excluirMusica(IdRequest request, StreamObserver<Empty> responseObserver) {
        responder(responseObserver, () -> { service.excluirMusica(request.getId()); return Empty.getDefaultInstance(); });
    }

    @Override
    public void listarPlaylists(Empty request, StreamObserver<PlaylistsResponse> responseObserver) {
        responder(responseObserver, () -> PlaylistsResponse.newBuilder()
                .addAllPlaylists(service.listarPlaylists().stream().map(this::playlist).toList()).build());
    }

    @Override
    public void buscarPlaylist(IdRequest request, StreamObserver<Playlist> responseObserver) {
        responder(responseObserver, () -> playlist(service.buscarPlaylist(request.getId())));
    }

    @Override
    public void criarPlaylist(PlaylistRequest request, StreamObserver<Playlist> responseObserver) {
        responder(responseObserver, () -> playlist(service.criarPlaylist(playlistRequest(request))));
    }

    @Override
    public void atualizarPlaylist(AtualizarPlaylistRequest request, StreamObserver<Playlist> responseObserver) {
        responder(responseObserver, () -> playlist(service.atualizarPlaylist(request.getId(), playlistRequest(request.getInput()))));
    }

    @Override
    public void excluirPlaylist(IdRequest request, StreamObserver<Empty> responseObserver) {
        responder(responseObserver, () -> { service.excluirPlaylist(request.getId()); return Empty.getDefaultInstance(); });
    }

    @Override
    public void listarPlaylistsDoUsuario(IdRequest request, StreamObserver<PlaylistsResponse> responseObserver) {
        responder(responseObserver, () -> PlaylistsResponse.newBuilder()
                .addAllPlaylists(service.playlistsDoUsuario(request.getId()).stream().map(this::playlist).toList()).build());
    }

    @Override
    public void listarMusicasDaPlaylist(IdRequest request, StreamObserver<MusicasResponse> responseObserver) {
        responder(responseObserver, () -> MusicasResponse.newBuilder()
                .addAllMusicas(service.musicasDaPlaylist(request.getId()).stream().map(this::musica).toList()).build());
    }

    @Override
    public void listarPlaylistsDaMusica(IdRequest request, StreamObserver<PlaylistsResponse> responseObserver) {
        responder(responseObserver, () -> PlaylistsResponse.newBuilder()
                .addAllPlaylists(service.playlistsDaMusica(request.getId()).stream().map(this::playlist).toList()).build());
    }

    private void responder(StreamObserver<?> observer, Supplier<?> operacao) {
        try {
            Object resposta = operacao.get();
            @SuppressWarnings("unchecked") StreamObserver<Object> typedObserver = (StreamObserver<Object>) observer;
            typedObserver.onNext(resposta);
            typedObserver.onCompleted();
        } catch (NoSuchElementException exception) {
            observer.onError(Status.NOT_FOUND.withDescription(exception.getMessage()).asRuntimeException());
        } catch (RuntimeException exception) {
            observer.onError(Status.INTERNAL.withDescription("Erro ao executar a operação").withCause(exception).asRuntimeException());
        }
    }

    private com.example.demo.dto.PlaylistRequest playlistRequest(PlaylistRequest request) {
        return new com.example.demo.dto.PlaylistRequest(request.getNome(), request.getUsuarioId(), new java.util.HashSet<>(request.getMusicaIdsList()));
    }

    private Usuario usuario(UsuarioResponse response) {
        return Usuario.newBuilder().setId(response.id()).setNome(response.nome()).setIdade(response.idade()).build();
    }

    private Musica musica(MusicaResponse response) {
        return Musica.newBuilder().setId(response.id()).setNome(response.nome()).setArtista(response.artista()).build();
    }

    private Playlist playlist(PlaylistResponse response) {
        return Playlist.newBuilder().setId(response.id()).setNome(response.nome()).setUsuarioId(response.usuarioId())
                .addAllMusicaIds(response.musicaIds()).build();
    }
}

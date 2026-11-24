package com.example.demo.service;

import com.example.demo.dto.MusicaRequest;
import com.example.demo.dto.MusicaResponse;
import com.example.demo.dto.PlaylistRequest;
import com.example.demo.dto.PlaylistResponse;
import com.example.demo.dto.UsuarioRequest;
import com.example.demo.dto.UsuarioResponse;
import com.example.demo.model.Musica;
import com.example.demo.model.Playlist;
import com.example.demo.model.Usuario;
import com.example.demo.repository.MusicaRepository;
import com.example.demo.repository.PlaylistRepository;
import com.example.demo.repository.UsuarioRepository;
import jakarta.transaction.Transactional;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
@Transactional
public class CatalogoService {

    private final UsuarioRepository usuarios;
    private final MusicaRepository musicas;
    private final PlaylistRepository playlists;

    public CatalogoService(UsuarioRepository usuarios, MusicaRepository musicas, PlaylistRepository playlists) {
        this.usuarios = usuarios;
        this.musicas = musicas;
        this.playlists = playlists;
    }

    public List<UsuarioResponse> listarUsuarios() {
        return usuarios.findAll().stream().map(this::usuarioResponse).toList();
    }

    public UsuarioResponse buscarUsuario(Long id) {
        return usuarioResponse(usuario(id));
    }

    public UsuarioResponse criarUsuario(UsuarioRequest request) {
        Usuario usuario = new Usuario();
        atualizar(usuario, request);
        return usuarioResponse(usuarios.save(usuario));
    }

    public UsuarioResponse atualizarUsuario(Long id, UsuarioRequest request) {
        Usuario usuario = usuario(id);
        atualizar(usuario, request);
        return usuarioResponse(usuarios.save(usuario));
    }

    public void excluirUsuario(Long id) {
        usuarios.delete(usuario(id));
    }

    public List<MusicaResponse> listarMusicas() {
        return musicas.findAll().stream().map(this::musicaResponse).toList();
    }

    public MusicaResponse buscarMusica(Long id) {
        return musicaResponse(musica(id));
    }

    public MusicaResponse criarMusica(MusicaRequest request) {
        Musica musica = new Musica();
        atualizar(musica, request);
        return musicaResponse(musicas.save(musica));
    }

    public MusicaResponse atualizarMusica(Long id, MusicaRequest request) {
        Musica musica = musica(id);
        atualizar(musica, request);
        return musicaResponse(musicas.save(musica));
    }

    @Transactional
    public void excluirMusica(Long id) {
        Musica musica = musica(id);
        playlists.findByMusicasId(id).forEach(playlist -> playlist.getMusicas().remove(musica));
        musicas.delete(musica);
    }

    public List<PlaylistResponse> listarPlaylists() {
        return playlists.findAll().stream().map(this::playlistResponse).toList();
    }

    public PlaylistResponse buscarPlaylist(Long id) {
        return playlistResponse(playlist(id));
    }

    @Transactional
    public PlaylistResponse criarPlaylist(PlaylistRequest request) {
        Playlist playlist = new Playlist();
        atualizar(playlist, request);
        return playlistResponse(playlists.save(playlist));
    }

    @Transactional
    public PlaylistResponse atualizarPlaylist(Long id, PlaylistRequest request) {
        Playlist playlist = playlist(id);
        atualizar(playlist, request);
        return playlistResponse(playlists.save(playlist));
    }

    public void excluirPlaylist(Long id) {
        playlists.delete(playlist(id));
    }

    public List<PlaylistResponse> playlistsDoUsuario(Long usuarioId) {
        usuario(usuarioId);
        return playlists.findByUsuarioId(usuarioId).stream().map(this::playlistResponse).toList();
    }

    public List<MusicaResponse> musicasDaPlaylist(Long playlistId) {
        return playlist(playlistId).getMusicas().stream().map(this::musicaResponse).toList();
    }

    public List<PlaylistResponse> playlistsDaMusica(Long musicaId) {
        musica(musicaId);
        return playlists.findByMusicasId(musicaId).stream().map(this::playlistResponse).toList();
    }

    private void atualizar(Usuario usuario, UsuarioRequest request) {
        usuario.setNome(request.nome());
        usuario.setIdade(request.idade());
    }

    private void atualizar(Musica musica, MusicaRequest request) {
        musica.setNome(request.nome());
        musica.setArtista(request.artista());
    }

    private void atualizar(Playlist playlist, PlaylistRequest request) {
        playlist.setNome(request.nome());
        playlist.setUsuario(usuario(request.usuarioId()));
        Set<Musica> musicasDaPlaylist = new HashSet<>();
        if (request.musicaIds() != null) {
            request.musicaIds().forEach(id -> musicasDaPlaylist.add(musica(id)));
        }
        playlist.setMusicas(musicasDaPlaylist);
    }

    private Usuario usuario(Long id) {
        return usuarios.findById(id).orElseThrow(() -> naoEncontrado("Usuário", id));
    }

    private Musica musica(Long id) {
        return musicas.findById(id).orElseThrow(() -> naoEncontrado("Música", id));
    }

    private Playlist playlist(Long id) {
        return playlists.findById(id).orElseThrow(() -> naoEncontrado("Playlist", id));
    }

    private ResponseStatusException naoEncontrado(String recurso, Long id) {
        return new ResponseStatusException(HttpStatus.NOT_FOUND, recurso + " " + id + " não encontrado");
    }

    private UsuarioResponse usuarioResponse(Usuario usuario) {
        return new UsuarioResponse(usuario.getId(), usuario.getNome(), usuario.getIdade());
    }

    private MusicaResponse musicaResponse(Musica musica) {
        return new MusicaResponse(musica.getId(), musica.getNome(), musica.getArtista());
    }

    private PlaylistResponse playlistResponse(Playlist playlist) {
        Set<Long> musicaIds = playlist.getMusicas().stream().map(Musica::getId).collect(java.util.stream.Collectors.toSet());
        return new PlaylistResponse(playlist.getId(), playlist.getNome(), playlist.getUsuario().getId(), musicaIds);
    }
}

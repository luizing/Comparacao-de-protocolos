package com.example.demo.controller;

import com.example.demo.dto.MusicaRequest;
import com.example.demo.dto.MusicaResponse;
import com.example.demo.dto.PlaylistRequest;
import com.example.demo.dto.PlaylistResponse;
import com.example.demo.dto.UsuarioRequest;
import com.example.demo.dto.UsuarioResponse;
import com.example.demo.service.CatalogoService;
import java.util.List;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.stereotype.Controller;

/** Ponto de entrada GraphQL para o catálogo de músicas. */
@Controller
public class CatalogoGraphqlController {

    private final CatalogoService service;

    public CatalogoGraphqlController(CatalogoService service) {
        this.service = service;
    }

    @QueryMapping
    public List<UsuarioResponse> usuarios() {
        return service.listarUsuarios();
    }

    @QueryMapping
    public UsuarioResponse usuario(@Argument("id") Long id) {
        return service.buscarUsuario(id);
    }

    @QueryMapping
    public List<MusicaResponse> musicas() {
        return service.listarMusicas();
    }

    @QueryMapping
    public MusicaResponse musica(@Argument("id") Long id) {
        return service.buscarMusica(id);
    }

    @QueryMapping
    public List<PlaylistResponse> playlists() {
        return service.listarPlaylists();
    }

    @QueryMapping
    public PlaylistResponse playlist(@Argument("id") Long id) {
        return service.buscarPlaylist(id);
    }

    @QueryMapping
    public List<PlaylistResponse> playlistsDoUsuario(@Argument("usuarioId") Long usuarioId) {
        return service.playlistsDoUsuario(usuarioId);
    }

    @QueryMapping
    public List<MusicaResponse> musicasDaPlaylist(@Argument("playlistId") Long playlistId) {
        return service.musicasDaPlaylist(playlistId);
    }

    @QueryMapping
    public List<PlaylistResponse> playlistsDaMusica(@Argument("musicaId") Long musicaId) {
        return service.playlistsDaMusica(musicaId);
    }

    @MutationMapping
    public UsuarioResponse criarUsuario(@Argument("input") UsuarioRequest input) {
        return service.criarUsuario(input);
    }

    @MutationMapping
    public UsuarioResponse atualizarUsuario(@Argument("id") Long id, @Argument("input") UsuarioRequest input) {
        return service.atualizarUsuario(id, input);
    }

    @MutationMapping
    public Boolean excluirUsuario(@Argument("id") Long id) {
        service.excluirUsuario(id);
        return true;
    }

    @MutationMapping
    public MusicaResponse criarMusica(@Argument("input") MusicaRequest input) {
        return service.criarMusica(input);
    }

    @MutationMapping
    public MusicaResponse atualizarMusica(@Argument("id") Long id, @Argument("input") MusicaRequest input) {
        return service.atualizarMusica(id, input);
    }

    @MutationMapping
    public Boolean excluirMusica(@Argument("id") Long id) {
        service.excluirMusica(id);
        return true;
    }

    @MutationMapping
    public PlaylistResponse criarPlaylist(@Argument("input") PlaylistRequest input) {
        return service.criarPlaylist(input);
    }

    @MutationMapping
    public PlaylistResponse atualizarPlaylist(@Argument("id") Long id, @Argument("input") PlaylistRequest input) {
        return service.atualizarPlaylist(id, input);
    }

    @MutationMapping
    public Boolean excluirPlaylist(@Argument("id") Long id) {
        service.excluirPlaylist(id);
        return true;
    }
}

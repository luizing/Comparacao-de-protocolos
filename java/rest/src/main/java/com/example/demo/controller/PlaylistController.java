package com.example.demo.controller;

import com.example.demo.dto.MusicaResponse;
import com.example.demo.dto.PlaylistRequest;
import com.example.demo.dto.PlaylistResponse;
import com.example.demo.service.CatalogoService;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/playlists")
public class PlaylistController {
    private final CatalogoService service;
    public PlaylistController(CatalogoService service) { this.service = service; }
    @GetMapping public List<PlaylistResponse> listar() { return service.listarPlaylists(); }
    @GetMapping("/{id}") public PlaylistResponse buscar(@PathVariable Long id) { return service.buscarPlaylist(id); }
    @PostMapping @ResponseStatus(HttpStatus.CREATED) public PlaylistResponse criar(@RequestBody PlaylistRequest request) { return service.criarPlaylist(request); }
    @PutMapping("/{id}") public PlaylistResponse atualizar(@PathVariable Long id, @RequestBody PlaylistRequest request) { return service.atualizarPlaylist(id, request); }
    @DeleteMapping("/{id}") @ResponseStatus(HttpStatus.NO_CONTENT) public void excluir(@PathVariable Long id) { service.excluirPlaylist(id); }
    @GetMapping("/{id}/musicas") public List<MusicaResponse> musicas(@PathVariable Long id) { return service.musicasDaPlaylist(id); }
}

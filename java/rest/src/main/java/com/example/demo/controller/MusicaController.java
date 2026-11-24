package com.example.demo.controller;

import com.example.demo.dto.MusicaRequest;
import com.example.demo.dto.MusicaResponse;
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
@RequestMapping("/api/musicas")
public class MusicaController {
    private final CatalogoService service;
    public MusicaController(CatalogoService service) { this.service = service; }
    @GetMapping public List<MusicaResponse> listar() { return service.listarMusicas(); }
    @GetMapping("/{id}") public MusicaResponse buscar(@PathVariable Long id) { return service.buscarMusica(id); }
    @PostMapping @ResponseStatus(HttpStatus.CREATED) public MusicaResponse criar(@RequestBody MusicaRequest request) { return service.criarMusica(request); }
    @PutMapping("/{id}") public MusicaResponse atualizar(@PathVariable Long id, @RequestBody MusicaRequest request) { return service.atualizarMusica(id, request); }
    @DeleteMapping("/{id}") @ResponseStatus(HttpStatus.NO_CONTENT) public void excluir(@PathVariable Long id) { service.excluirMusica(id); }
    @GetMapping("/{id}/playlists") public List<PlaylistResponse> playlists(@PathVariable Long id) { return service.playlistsDaMusica(id); }
}

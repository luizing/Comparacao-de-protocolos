package com.example.demo.controller;

import com.example.demo.dto.PlaylistResponse;
import com.example.demo.dto.UsuarioRequest;
import com.example.demo.dto.UsuarioResponse;
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
@RequestMapping("/api/usuarios")
public class UsuarioController {
    private final CatalogoService service;
    public UsuarioController(CatalogoService service) { this.service = service; }
    @GetMapping public List<UsuarioResponse> listar() { return service.listarUsuarios(); }
    @GetMapping("/{id}") public UsuarioResponse buscar(@PathVariable Long id) { return service.buscarUsuario(id); }
    @PostMapping @ResponseStatus(HttpStatus.CREATED) public UsuarioResponse criar(@RequestBody UsuarioRequest request) { return service.criarUsuario(request); }
    @PutMapping("/{id}") public UsuarioResponse atualizar(@PathVariable Long id, @RequestBody UsuarioRequest request) { return service.atualizarUsuario(id, request); }
    @DeleteMapping("/{id}") @ResponseStatus(HttpStatus.NO_CONTENT) public void excluir(@PathVariable Long id) { service.excluirUsuario(id); }
    @GetMapping("/{id}/playlists") public List<PlaylistResponse> playlists(@PathVariable Long id) { return service.playlistsDoUsuario(id); }
}

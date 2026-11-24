package com.example.demo.dto;

import java.util.Set;

public record PlaylistResponse(Long id, String nome, Long usuarioId, Set<Long> musicaIds) {
}

package com.example.demo.dto;

import java.util.Set;

public record PlaylistRequest(String nome, Long usuarioId, Set<Long> musicaIds) {
}

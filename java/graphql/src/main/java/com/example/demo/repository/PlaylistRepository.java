package com.example.demo.repository;

import com.example.demo.model.Playlist;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PlaylistRepository extends JpaRepository<Playlist, Long> {
    List<Playlist> findByUsuarioId(Long usuarioId);
    List<Playlist> findByMusicasId(Long musicaId);
}

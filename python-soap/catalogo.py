"""Regras de negócio do serviço de streaming (equivalente ao CatalogoService do Java).

Banco SQLite em memória, assim como o H2 em memória da versão Java.
"""
import sqlite3
import threading


class NaoEncontrado(Exception):
    pass


class Catalogo:
    def __init__(self):
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.db.execute("PRAGMA foreign_keys = ON")
        self.lock = threading.Lock()
        self.db.executescript(
            """
            CREATE TABLE usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                idade INTEGER
            );
            CREATE TABLE musica (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                artista TEXT
            );
            CREATE TABLE playlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                usuario_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE
            );
            CREATE TABLE playlist_musica (
                playlist_id INTEGER REFERENCES playlist(id) ON DELETE CASCADE,
                musica_id INTEGER REFERENCES musica(id) ON DELETE CASCADE,
                PRIMARY KEY (playlist_id, musica_id)
            );
            """
        )

    # ---------- auxiliares ----------
    def _um(self, sql, params=()):
        return self.db.execute(sql, params).fetchone()

    def _todos(self, sql, params=()):
        return self.db.execute(sql, params).fetchall()

    def _existe(self, tabela, nome, id):
        if self._um(f"SELECT 1 FROM {tabela} WHERE id = ?", (id,)) is None:
            raise NaoEncontrado(f"{nome} {id} não encontrado")

    @staticmethod
    def _usuario(row):
        return {"id": row[0], "nome": row[1], "idade": row[2]}

    @staticmethod
    def _musica(row):
        return {"id": row[0], "nome": row[1], "artista": row[2]}

    def _playlist(self, row):
        ids = [r[0] for r in self._todos(
            "SELECT musica_id FROM playlist_musica WHERE playlist_id = ? ORDER BY musica_id", (row[0],))]
        return {"id": row[0], "nome": row[1], "usuarioId": row[2], "musicaIds": ids}

    # ---------- usuários ----------
    def listar_usuarios(self):
        with self.lock:
            return [self._usuario(r) for r in self._todos("SELECT id, nome, idade FROM usuario")]

    def buscar_usuario(self, id):
        with self.lock:
            self._existe("usuario", "Usuário", id)
            return self._usuario(self._um("SELECT id, nome, idade FROM usuario WHERE id = ?", (id,)))

    def criar_usuario(self, nome, idade):
        with self.lock, self.db:
            cur = self.db.execute("INSERT INTO usuario (nome, idade) VALUES (?, ?)", (nome, idade))
            return {"id": cur.lastrowid, "nome": nome, "idade": idade}

    def atualizar_usuario(self, id, nome, idade):
        with self.lock, self.db:
            self._existe("usuario", "Usuário", id)
            self.db.execute("UPDATE usuario SET nome = ?, idade = ? WHERE id = ?", (nome, idade, id))
            return {"id": id, "nome": nome, "idade": idade}

    def excluir_usuario(self, id):
        with self.lock, self.db:
            self._existe("usuario", "Usuário", id)
            self.db.execute("DELETE FROM usuario WHERE id = ?", (id,))

    # ---------- músicas ----------
    def listar_musicas(self):
        with self.lock:
            return [self._musica(r) for r in self._todos("SELECT id, nome, artista FROM musica")]

    def buscar_musica(self, id):
        with self.lock:
            self._existe("musica", "Música", id)
            return self._musica(self._um("SELECT id, nome, artista FROM musica WHERE id = ?", (id,)))

    def criar_musica(self, nome, artista):
        with self.lock, self.db:
            cur = self.db.execute("INSERT INTO musica (nome, artista) VALUES (?, ?)", (nome, artista))
            return {"id": cur.lastrowid, "nome": nome, "artista": artista}

    def atualizar_musica(self, id, nome, artista):
        with self.lock, self.db:
            self._existe("musica", "Música", id)
            self.db.execute("UPDATE musica SET nome = ?, artista = ? WHERE id = ?", (nome, artista, id))
            return {"id": id, "nome": nome, "artista": artista}

    def excluir_musica(self, id):
        with self.lock, self.db:
            self._existe("musica", "Música", id)
            self.db.execute("DELETE FROM musica WHERE id = ?", (id,))

    # ---------- playlists ----------
    def listar_playlists(self):
        with self.lock:
            return [self._playlist(r) for r in self._todos("SELECT id, nome, usuario_id FROM playlist")]

    def buscar_playlist(self, id):
        with self.lock:
            self._existe("playlist", "Playlist", id)
            return self._playlist(self._um("SELECT id, nome, usuario_id FROM playlist WHERE id = ?", (id,)))

    def _validar_playlist(self, usuario_id, musica_ids):
        self._existe("usuario", "Usuário", usuario_id)
        for mid in musica_ids or []:
            self._existe("musica", "Música", mid)

    def _gravar_musicas(self, playlist_id, musica_ids):
        self.db.execute("DELETE FROM playlist_musica WHERE playlist_id = ?", (playlist_id,))
        self.db.executemany(
            "INSERT INTO playlist_musica (playlist_id, musica_id) VALUES (?, ?)",
            [(playlist_id, mid) for mid in set(musica_ids or [])],
        )

    def criar_playlist(self, nome, usuario_id, musica_ids):
        with self.lock, self.db:
            self._validar_playlist(usuario_id, musica_ids)
            cur = self.db.execute("INSERT INTO playlist (nome, usuario_id) VALUES (?, ?)", (nome, usuario_id))
            self._gravar_musicas(cur.lastrowid, musica_ids)
            return self._playlist((cur.lastrowid, nome, usuario_id))

    def atualizar_playlist(self, id, nome, usuario_id, musica_ids):
        with self.lock, self.db:
            self._existe("playlist", "Playlist", id)
            self._validar_playlist(usuario_id, musica_ids)
            self.db.execute("UPDATE playlist SET nome = ?, usuario_id = ? WHERE id = ?", (nome, usuario_id, id))
            self._gravar_musicas(id, musica_ids)
            return self._playlist((id, nome, usuario_id))

    def excluir_playlist(self, id):
        with self.lock, self.db:
            self._existe("playlist", "Playlist", id)
            self.db.execute("DELETE FROM playlist WHERE id = ?", (id,))

    # ---------- consultas pedidas no enunciado ----------
    def playlists_do_usuario(self, usuario_id):
        with self.lock:
            self._existe("usuario", "Usuário", usuario_id)
            rows = self._todos("SELECT id, nome, usuario_id FROM playlist WHERE usuario_id = ?", (usuario_id,))
            return [self._playlist(r) for r in rows]

    def musicas_da_playlist(self, playlist_id):
        with self.lock:
            self._existe("playlist", "Playlist", playlist_id)
            rows = self._todos(
                "SELECT m.id, m.nome, m.artista FROM musica m "
                "JOIN playlist_musica pm ON pm.musica_id = m.id WHERE pm.playlist_id = ?",
                (playlist_id,),
            )
            return [self._musica(r) for r in rows]

    def playlists_da_musica(self, musica_id):
        with self.lock:
            self._existe("musica", "Música", musica_id)
            rows = self._todos(
                "SELECT p.id, p.nome, p.usuario_id FROM playlist p "
                "JOIN playlist_musica pm ON pm.playlist_id = p.id WHERE pm.musica_id = ?",
                (musica_id,),
            )
            return [self._playlist(r) for r in rows]

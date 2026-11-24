package com.example.demo.soap;

import com.example.demo.dto.MusicaRequest;
import com.example.demo.dto.MusicaResponse;
import com.example.demo.dto.PlaylistRequest;
import com.example.demo.dto.PlaylistResponse;
import com.example.demo.dto.UsuarioRequest;
import com.example.demo.dto.UsuarioResponse;
import com.example.demo.service.CatalogoService;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import javax.xml.parsers.DocumentBuilderFactory;
import org.springframework.ws.server.endpoint.annotation.Endpoint;
import org.springframework.ws.server.endpoint.annotation.PayloadRoot;
import org.springframework.ws.server.endpoint.annotation.RequestPayload;
import org.springframework.ws.server.endpoint.annotation.ResponsePayload;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

@Endpoint
public class StreamingEndpoint {

    public static final String NAMESPACE = "http://example.com/demo/streaming";
    private final CatalogoService service;

    public StreamingEndpoint(CatalogoService service) {
        this.service = service;
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "ListarUsuariosRequest")
    @ResponsePayload
    public Element listarUsuarios(@RequestPayload Element request) {
        return usuarios("ListarUsuariosResponse", service.listarUsuarios());
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "BuscarUsuarioRequest")
    @ResponsePayload
    public Element buscarUsuario(@RequestPayload Element request) {
        return usuario("BuscarUsuarioResponse", service.buscarUsuario(id(request)));
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "CriarUsuarioRequest")
    @ResponsePayload
    public Element criarUsuario(@RequestPayload Element request) {
        return usuario("CriarUsuarioResponse", service.criarUsuario(usuarioRequest(request)));
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "AtualizarUsuarioRequest")
    @ResponsePayload
    public Element atualizarUsuario(@RequestPayload Element request) {
        return usuario("AtualizarUsuarioResponse", service.atualizarUsuario(id(request), usuarioRequest(request)));
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "ExcluirUsuarioRequest")
    @ResponsePayload
    public Element excluirUsuario(@RequestPayload Element request) {
        service.excluirUsuario(id(request));
        return root("ExcluirUsuarioResponse");
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "ListarMusicasRequest")
    @ResponsePayload
    public Element listarMusicas(@RequestPayload Element request) {
        return musicas("ListarMusicasResponse", service.listarMusicas());
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "BuscarMusicaRequest")
    @ResponsePayload
    public Element buscarMusica(@RequestPayload Element request) {
        return musica("BuscarMusicaResponse", service.buscarMusica(id(request)));
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "CriarMusicaRequest")
    @ResponsePayload
    public Element criarMusica(@RequestPayload Element request) {
        return musica("CriarMusicaResponse", service.criarMusica(musicaRequest(request)));
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "AtualizarMusicaRequest")
    @ResponsePayload
    public Element atualizarMusica(@RequestPayload Element request) {
        return musica("AtualizarMusicaResponse", service.atualizarMusica(id(request), musicaRequest(request)));
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "ExcluirMusicaRequest")
    @ResponsePayload
    public Element excluirMusica(@RequestPayload Element request) {
        service.excluirMusica(id(request));
        return root("ExcluirMusicaResponse");
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "ListarPlaylistsRequest")
    @ResponsePayload
    public Element listarPlaylists(@RequestPayload Element request) {
        return playlists("ListarPlaylistsResponse", service.listarPlaylists());
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "BuscarPlaylistRequest")
    @ResponsePayload
    public Element buscarPlaylist(@RequestPayload Element request) {
        return playlist("BuscarPlaylistResponse", service.buscarPlaylist(id(request)));
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "CriarPlaylistRequest")
    @ResponsePayload
    public Element criarPlaylist(@RequestPayload Element request) {
        return playlist("CriarPlaylistResponse", service.criarPlaylist(playlistRequest(request)));
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "AtualizarPlaylistRequest")
    @ResponsePayload
    public Element atualizarPlaylist(@RequestPayload Element request) {
        return playlist("AtualizarPlaylistResponse", service.atualizarPlaylist(id(request), playlistRequest(request)));
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "ExcluirPlaylistRequest")
    @ResponsePayload
    public Element excluirPlaylist(@RequestPayload Element request) {
        service.excluirPlaylist(id(request));
        return root("ExcluirPlaylistResponse");
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "PlaylistsDoUsuarioRequest")
    @ResponsePayload
    public Element playlistsDoUsuario(@RequestPayload Element request) {
        return playlists("PlaylistsDoUsuarioResponse", service.playlistsDoUsuario(id(request)));
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "MusicasDaPlaylistRequest")
    @ResponsePayload
    public Element musicasDaPlaylist(@RequestPayload Element request) {
        return musicas("MusicasDaPlaylistResponse", service.musicasDaPlaylist(id(request)));
    }

    @PayloadRoot(namespace = NAMESPACE, localPart = "PlaylistsDaMusicaRequest")
    @ResponsePayload
    public Element playlistsDaMusica(@RequestPayload Element request) {
        return playlists("PlaylistsDaMusicaResponse", service.playlistsDaMusica(id(request)));
    }

    private UsuarioRequest usuarioRequest(Element request) {
        return new UsuarioRequest(texto(request, "nome"), Integer.valueOf(texto(request, "idade")));
    }

    private MusicaRequest musicaRequest(Element request) {
        return new MusicaRequest(texto(request, "nome"), texto(request, "artista"));
    }

    private PlaylistRequest playlistRequest(Element request) {
        Set<Long> musicaIds = new LinkedHashSet<>();
        for (Element element : filhos(request, "musicaId")) {
            musicaIds.add(Long.valueOf(element.getTextContent()));
        }
        return new PlaylistRequest(texto(request, "nome"), Long.valueOf(texto(request, "usuarioId")), musicaIds);
    }

    private Long id(Element request) {
        return Long.valueOf(texto(request, "id"));
    }

    private String texto(Element parent, String nome) {
        List<Element> filhos = filhos(parent, nome);
        if (filhos.isEmpty()) {
            throw new IllegalArgumentException("Campo SOAP obrigatório ausente: " + nome);
        }
        return filhos.get(0).getTextContent();
    }

    private List<Element> filhos(Element parent, String nome) {
        NodeList nodes = parent.getChildNodes();
        java.util.ArrayList<Element> encontrados = new java.util.ArrayList<>();
        for (int i = 0; i < nodes.getLength(); i++) {
            Node node = nodes.item(i);
            if (node instanceof Element element && nome.equals(element.getLocalName())) {
                encontrados.add(element);
            }
        }
        return encontrados;
    }

    private Element usuarios(String resposta, List<UsuarioResponse> valores) {
        Element root = root(resposta);
        valores.forEach(valor -> adicionarUsuario(root, valor));
        return root;
    }

    private Element usuario(String resposta, UsuarioResponse valor) {
        Element root = root(resposta);
        adicionarUsuario(root, valor);
        return root;
    }

    private Element musicas(String resposta, List<MusicaResponse> valores) {
        Element root = root(resposta);
        valores.forEach(valor -> adicionarMusica(root, valor));
        return root;
    }

    private Element musica(String resposta, MusicaResponse valor) {
        Element root = root(resposta);
        adicionarMusica(root, valor);
        return root;
    }

    private Element playlists(String resposta, List<PlaylistResponse> valores) {
        Element root = root(resposta);
        valores.forEach(valor -> adicionarPlaylist(root, valor));
        return root;
    }

    private Element playlist(String resposta, PlaylistResponse valor) {
        Element root = root(resposta);
        adicionarPlaylist(root, valor);
        return root;
    }

    private Element root(String nome) {
        try {
            Document document = DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument();
            Element root = document.createElementNS(NAMESPACE, "st:" + nome);
            root.setAttribute("xmlns:st", NAMESPACE);
            document.appendChild(root);
            return root;
        } catch (Exception exception) {
            throw new IllegalStateException("Não foi possível criar a resposta SOAP", exception);
        }
    }

    private void adicionarUsuario(Element parent, UsuarioResponse valor) {
        Element usuario = adicionar(parent, "usuario", null);
        adicionar(usuario, "id", valor.id());
        adicionar(usuario, "nome", valor.nome());
        adicionar(usuario, "idade", valor.idade());
    }

    private void adicionarMusica(Element parent, MusicaResponse valor) {
        Element musica = adicionar(parent, "musica", null);
        adicionar(musica, "id", valor.id());
        adicionar(musica, "nome", valor.nome());
        adicionar(musica, "artista", valor.artista());
    }

    private void adicionarPlaylist(Element parent, PlaylistResponse valor) {
        Element playlist = adicionar(parent, "playlist", null);
        adicionar(playlist, "id", valor.id());
        adicionar(playlist, "nome", valor.nome());
        adicionar(playlist, "usuarioId", valor.usuarioId());
        valor.musicaIds().forEach(musicaId -> adicionar(playlist, "musicaId", musicaId));
    }

    private Element adicionar(Element parent, String nome, Object valor) {
        Element child = parent.getOwnerDocument().createElementNS(NAMESPACE, "st:" + nome);
        if (valor != null) {
            child.setTextContent(String.valueOf(valor));
        }
        parent.appendChild(child);
        return child;
    }
}

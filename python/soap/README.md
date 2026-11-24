# Streaming de Músicas: SOAP em Python

Versão SOAP 1.1 do serviço em Python, no estilo document/literal wrapped.
**O contrato é idêntico ao da versão Java** (branch `soap`, `streaming.xsd`): mesmo namespace, mesmos elementos `<Operacao>Request` e `<Operacao>Response`, mesmos campos e mesmo caminho `/ws`. Um cliente feito para uma versão funciona com a outra.

O servidor foi feito com FastAPI e lxml. O WSDL é gerado a partir da tabela de operações em `main.py`.
Por que não usamos o Spyne: a última versão dele (2.14) não funciona no Python 3.12 e a biblioteca está sem manutenção.

## Como rodar

```bash
cd python/soap
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python main.py                # sobe em http://localhost:8003
```

- WSDL: `http://localhost:8003/ws/streaming.wsdl`
- Endpoint: `POST http://localhost:8003/ws`

Em outro terminal, também com o `.venv` ativado:

```bash
python client.py              # cliente zeep: lê o WSDL e executa o CRUD completo
```

## Exemplo de requisição (igual ao da versão Java)

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:st="http://example.com/demo/streaming">
  <soapenv:Body>
    <st:CriarPlaylistRequest>
      <st:nome>Favoritas</st:nome>
      <st:usuarioId>1</st:usuarioId>
      <st:musicaId>1</st:musicaId>
      <st:musicaId>2</st:musicaId>
    </st:CriarPlaylistRequest>
  </soapenv:Body>
</soapenv:Envelope>
```

## Operações

`ListarUsuarios`, `BuscarUsuario`, `CriarUsuario`, `AtualizarUsuario`, `ExcluirUsuario`. As mesmas existem para Músicas e Playlists.

Consultas do enunciado (todas recebem `<st:id>`): `PlaylistsDoUsuario`, `MusicasDaPlaylist`, `PlaylistsDaMusica`.

Quando o id não existe, o servidor responde com um `soapenv:Fault` e HTTP 500, como manda o SOAP 1.1.

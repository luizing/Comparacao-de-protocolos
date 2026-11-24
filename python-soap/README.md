# Streaming de Músicas: SOAP em Python

Versão SOAP 1.1 do serviço em Python, no estilo document/literal wrapped (o mesmo do Spring Web Services).
O servidor foi feito com FastAPI e lxml. O WSDL é gerado a partir da tabela de operações em `main.py`.

Por que não usamos o Spyne: a última versão dele (2.14) não funciona no Python 3.12 e a biblioteca está sem manutenção. Por isso o envelope SOAP é montado e lido direto com lxml, o que também deixa o formato das mensagens bem visível.

## Como rodar

```bash
cd python-soap
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python main.py                # sobe em http://localhost:8000
```

- WSDL: `http://localhost:8000/soap?wsdl`
- Endpoint: `POST http://localhost:8000/soap`

Em outro terminal, também com o `.venv` ativado:

```bash
python client.py              # cliente zeep: lê o WSDL e executa o CRUD completo
```

Também dá para importar o WSDL no SoapUI ou no Postman.

## Exemplo de requisição

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:tns="http://streaming.example.com/soap">
  <soapenv:Body>
    <tns:CriarMusica>
      <tns:nome>Song A</tns:nome>
      <tns:artista>X</tns:artista>
    </tns:CriarMusica>
  </soapenv:Body>
</soapenv:Envelope>
```

## Operações

`ListarUsuarios`, `BuscarUsuario`, `CriarUsuario`, `AtualizarUsuario`, `ExcluirUsuario`. As mesmas existem para Músicas e Playlists.

Consultas do enunciado: `PlaylistsDoUsuario`, `MusicasDaPlaylist`, `PlaylistsDaMusica`.

Quando o id não existe, o servidor responde com um `soapenv:Fault` e HTTP 500, como manda o SOAP 1.1.

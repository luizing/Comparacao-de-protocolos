"""Serviço de streaming de músicas - versão SOAP 1.1 em Python (FastAPI + lxml).

Mesmo contrato da versão Java (Spring Web Services, streaming.xsd):
mesmo namespace, elementos <Operacao>Request/<Operacao>Response e campos.
  WSDL:     GET  http://localhost:8080/ws/streaming.wsdl
  Endpoint: POST http://localhost:8080/ws
"""
from fastapi import FastAPI, Request, Response
from lxml import etree

from catalogo import Catalogo, NaoEncontrado

SOAP_ENV = "http://schemas.xmlsoap.org/soap/envelope/"
TNS = "http://example.com/demo/streaming"
URL = "http://localhost:8080/ws"

service = Catalogo()

# ---------- tipos complexos (viram <xs:complexType> no WSDL) ----------
# campo: (nome, tipo xsd, repetido?)
TIPOS = {
    "Usuario": [("id", "long", False), ("nome", "string", False), ("idade", "int", False)],
    "Musica": [("id", "long", False), ("nome", "string", False), ("artista", "string", False)],
    "Playlist": [("id", "long", False), ("nome", "string", False), ("usuarioId", "long", False),
                 ("musicaId", "long", True)],
}

# nome do elemento XML -> chave no dicionário do catálogo
CHAVES = {"musicaId": "musicaIds"}

ID = [("id", "long", False)]
USUARIO_IN = [("nome", "string", False), ("idade", "int", False)]
MUSICA_IN = [("nome", "string", False), ("artista", "string", False)]
PLAYLIST_IN = [("nome", "string", False), ("usuarioId", "long", False), ("musicaId", "long", True)]

# ---------- operações ----------
# nome: (campos de entrada, (tipo de retorno, é lista?) ou None, função)
OPERACOES = {
    "ListarUsuarios": ([], ("Usuario", True), lambda a: service.listar_usuarios()),
    "BuscarUsuario": (ID, ("Usuario", False), lambda a: service.buscar_usuario(a["id"])),
    "CriarUsuario": (USUARIO_IN, ("Usuario", False), lambda a: service.criar_usuario(a["nome"], a["idade"])),
    "AtualizarUsuario": (ID + USUARIO_IN, ("Usuario", False),
                         lambda a: service.atualizar_usuario(a["id"], a["nome"], a["idade"])),
    "ExcluirUsuario": (ID, None, lambda a: service.excluir_usuario(a["id"])),

    "ListarMusicas": ([], ("Musica", True), lambda a: service.listar_musicas()),
    "BuscarMusica": (ID, ("Musica", False), lambda a: service.buscar_musica(a["id"])),
    "CriarMusica": (MUSICA_IN, ("Musica", False), lambda a: service.criar_musica(a["nome"], a["artista"])),
    "AtualizarMusica": (ID + MUSICA_IN, ("Musica", False),
                        lambda a: service.atualizar_musica(a["id"], a["nome"], a["artista"])),
    "ExcluirMusica": (ID, None, lambda a: service.excluir_musica(a["id"])),

    "ListarPlaylists": ([], ("Playlist", True), lambda a: service.listar_playlists()),
    "BuscarPlaylist": (ID, ("Playlist", False), lambda a: service.buscar_playlist(a["id"])),
    "CriarPlaylist": (PLAYLIST_IN, ("Playlist", False),
                      lambda a: service.criar_playlist(a["nome"], a["usuarioId"], a["musicaId"])),
    "AtualizarPlaylist": (ID + PLAYLIST_IN, ("Playlist", False),
                          lambda a: service.atualizar_playlist(a["id"], a["nome"], a["usuarioId"], a["musicaId"])),
    "ExcluirPlaylist": (ID, None, lambda a: service.excluir_playlist(a["id"])),

    # consultas pedidas no enunciado
    "PlaylistsDoUsuario": (ID, ("Playlist", True), lambda a: service.playlists_do_usuario(a["id"])),
    "MusicasDaPlaylist": (ID, ("Musica", True), lambda a: service.musicas_da_playlist(a["id"])),
    "PlaylistsDaMusica": (ID, ("Playlist", True), lambda a: service.playlists_da_musica(a["id"])),
}


# ---------- WSDL (gerado a partir das tabelas acima) ----------
VARIOS = ' maxOccurs="unbounded"'


def _sequencia(campos):
    return "".join(
        f'<xs:element name="{n}" type="xs:{t}" minOccurs="0"{VARIOS if rep else ""}/>'
        for n, t, rep in campos
    )


def gerar_wsdl():
    tipos = "".join(
        f'<xs:complexType name="{nome}"><xs:sequence>{_sequencia(c)}</xs:sequence></xs:complexType>'
        for nome, c in TIPOS.items()
    )
    elementos, mensagens, port_ops, binding_ops = [], [], [], []
    for op, (entrada, saida, _) in OPERACOES.items():
        elementos.append(f'<xs:element name="{op}Request"><xs:complexType><xs:sequence>'
                         f'{_sequencia(entrada)}</xs:sequence></xs:complexType></xs:element>')
        retorno = ""
        if saida:
            tipo, lista = saida
            retorno = (f'<xs:element name="{tipo.lower()}" type="tns:{tipo}" minOccurs="0"'
                       f'{VARIOS if lista else ""}/>')
        elementos.append(f'<xs:element name="{op}Response"><xs:complexType><xs:sequence>'
                         f'{retorno}</xs:sequence></xs:complexType></xs:element>')
        mensagens.append(f'<wsdl:message name="{op}Request"><wsdl:part name="parameters" element="tns:{op}Request"/></wsdl:message>'
                         f'<wsdl:message name="{op}Response"><wsdl:part name="parameters" element="tns:{op}Response"/></wsdl:message>')
        port_ops.append(f'<wsdl:operation name="{op}"><wsdl:input message="tns:{op}Request"/>'
                        f'<wsdl:output message="tns:{op}Response"/></wsdl:operation>')
        binding_ops.append(f'<wsdl:operation name="{op}"><soap:operation soapAction=""/>'
                           f'<wsdl:input><soap:body use="literal"/></wsdl:input>'
                           f'<wsdl:output><soap:body use="literal"/></wsdl:output></wsdl:operation>')
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tns="{TNS}" targetNamespace="{TNS}">
  <wsdl:types>
    <xs:schema targetNamespace="{TNS}" elementFormDefault="qualified">{tipos}{"".join(elementos)}</xs:schema>
  </wsdl:types>
  {"".join(mensagens)}
  <wsdl:portType name="StreamingPort">{"".join(port_ops)}</wsdl:portType>
  <wsdl:binding name="StreamingPortSoap11" type="tns:StreamingPort">
    <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
    {"".join(binding_ops)}
  </wsdl:binding>
  <wsdl:service name="StreamingPortService">
    <wsdl:port name="StreamingPortSoap11" binding="tns:StreamingPortSoap11"><soap:address location="{URL}"/></wsdl:port>
  </wsdl:service>
</wsdl:definitions>"""


WSDL = gerar_wsdl()


# ---------- conversão XML <-> Python ----------
CONVERSORES = {"long": int, "int": int, "string": str}


def ler_argumentos(elemento, campos):
    args = {}
    for nome, tipo, rep in campos:
        valores = [CONVERSORES[tipo](e.text or "") for e in elemento.findall(f"{{{TNS}}}{nome}")]
        args[nome] = valores if rep else (valores[0] if valores else None)
    return args


def escrever_objeto(pai, tag, tipo, dados):
    obj = etree.SubElement(pai, f"{{{TNS}}}{tag}")
    for nome, _, rep in TIPOS[tipo]:
        valor = dados.get(CHAVES.get(nome, nome))
        for v in (valor if rep else [valor]):
            if v is not None:
                etree.SubElement(obj, f"{{{TNS}}}{nome}").text = str(v)


def envelope():
    env = etree.Element(f"{{{SOAP_ENV}}}Envelope", nsmap={"soapenv": SOAP_ENV, "st": TNS})
    return env, etree.SubElement(env, f"{{{SOAP_ENV}}}Body")


def xml_response(env, status=200):
    corpo = etree.tostring(env, xml_declaration=True, encoding="UTF-8")
    return Response(content=corpo, status_code=status, media_type="text/xml; charset=utf-8")


def fault(codigo, mensagem):
    env, body = envelope()
    f = etree.SubElement(body, f"{{{SOAP_ENV}}}Fault")
    etree.SubElement(f, "faultcode").text = f"soapenv:{codigo}"
    etree.SubElement(f, "faultstring").text = mensagem
    return xml_response(env, 500)


# ---------- HTTP ----------
app = FastAPI(title="Streaming de Músicas - SOAP (Python)")


@app.get("/ws/streaming.wsdl")
def wsdl():
    return Response(content=WSDL, media_type="text/xml; charset=utf-8")


@app.post("/ws")
async def soap(request: Request):
    try:
        raiz = etree.fromstring(await request.body())
        requisicao = raiz.find(f"{{{SOAP_ENV}}}Body")[0]
    except Exception:
        return fault("Client", "Envelope SOAP inválido")

    nome = etree.QName(requisicao).localname
    op = nome[:-len("Request")] if nome.endswith("Request") else nome
    if op not in OPERACOES:
        return fault("Client", f"Operação desconhecida: {op}")
    entrada, saida, funcao = OPERACOES[op]

    try:
        resultado = funcao(ler_argumentos(requisicao, entrada))
    except NaoEncontrado as e:
        return fault("Client", str(e))

    env, body = envelope()
    resposta = etree.SubElement(body, f"{{{TNS}}}{op}Response")
    if saida:
        tipo, lista = saida
        for item in (resultado if lista else [resultado]):
            escrever_objeto(resposta, tipo.lower(), tipo, item)
    return xml_response(env)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

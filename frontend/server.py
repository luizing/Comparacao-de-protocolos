"""Servidor do frontend: serve a página e repassa as chamadas aos serviços.

- POST /proxy       repassa ao serviço REST, GraphQL ou SOAP a requisição que o
                    navegador já montou. Só é necessário por causa do CORS:
                    o corpo vai exatamente como foi montado na página.
- POST /grpc/{op}   ponte gRPC: o navegador não fala gRPC, então a ponte converte
                    o JSON em protobuf, chama o servidor gRPC e devolve JSON.
"""
import time
from pathlib import Path
from urllib.parse import urlparse

import grpc
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from google.protobuf import empty_pb2, json_format

import catalogo_pb2 as pb
import catalogo_pb2_grpc as pb_grpc

PASTA = Path(__file__).parent
HOSTS_PERMITIDOS = {"localhost", "127.0.0.1"}

app = FastAPI(title="Frontend - Streaming de Músicas")
http = httpx.AsyncClient(timeout=30)
canais = {}


@app.get("/")
def index():
    return FileResponse(PASTA / "index.html")


@app.post("/proxy")
async def proxy(req: Request):
    dados = await req.json()
    url = dados["url"]
    if urlparse(url).hostname not in HOSTS_PERMITIDOS:
        raise HTTPException(400, "Só é permitido chamar serviços em localhost")
    headers = {"Content-Type": dados["contentType"]} if dados.get("contentType") else {}
    if dados.get("soapAction") is not None:
        headers["SOAPAction"] = dados["soapAction"]
    inicio = time.perf_counter()
    try:
        r = await http.request(dados["metodo"], url, content=(dados.get("corpo") or "").encode("utf-8"),
                               headers=headers)
    except httpx.HTTPError as e:
        return {"status": 0, "corpo": f"Não foi possível conectar em {url}: {e}", "ms": 0}
    return {"status": r.status_code, "corpo": r.text, "ms": (time.perf_counter() - inicio) * 1000}


def _para_dict(mensagem):
    try:
        return json_format.MessageToDict(mensagem, always_print_fields_with_no_presence=True)
    except TypeError:  # versões antigas do protobuf
        return json_format.MessageToDict(mensagem, including_default_value_fields=True)


@app.post("/grpc/{op}")
async def ponte_grpc(op: str, req: Request):
    dados = await req.json()
    endereco = dados.get("endereco", "localhost:50051")
    if endereco.split(":")[0] not in HOSTS_PERMITIDOS:
        raise HTTPException(400, "Só é permitido chamar serviços em localhost")
    metodo = pb.DESCRIPTOR.services_by_name["Catalogo"].methods_by_name.get(op)
    if metodo is None:
        raise HTTPException(404, f"Operação gRPC desconhecida: {op}")

    classe = empty_pb2.Empty if metodo.input_type.full_name == "google.protobuf.Empty" else getattr(pb, metodo.input_type.name)
    requisicao = json_format.ParseDict(dados.get("corpo", {}), classe())
    if endereco not in canais:
        canais[endereco] = grpc.insecure_channel(endereco)
    stub = pb_grpc.CatalogoStub(canais[endereco])

    inicio = time.perf_counter()
    try:
        resposta = getattr(stub, op)(requisicao, timeout=10)
    except grpc.RpcError as e:
        return JSONResponse({
            "ok": False, "codigo": e.code().name, "erro": e.details(),
            "bytesRequisicao": requisicao.SerializeToString().hex(" "),
            "ms": (time.perf_counter() - inicio) * 1000,
        })
    return {
        "ok": True,
        "resposta": _para_dict(resposta),
        "bytesRequisicao": requisicao.SerializeToString().hex(" "),
        "bytesResposta": resposta.SerializeToString().hex(" "),
        "ms": (time.perf_counter() - inicio) * 1000,
    }


if __name__ == "__main__":
    import uvicorn

    print("Frontend em http://localhost:3000")
    uvicorn.run(app, host="127.0.0.1", port=3000)

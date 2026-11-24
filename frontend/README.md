# Frontend: um só para os 4 protocolos

Uma única página para fazer o CRUD de usuários, músicas e playlists e rodar as 3 consultas do enunciado. No topo você escolhe o protocolo (**REST, GraphQL, SOAP ou gRPC**) e o endereço do servidor.

- **O corpo da requisição é o mesmo para todos.** Os formulários sempre produzem os mesmos dados, por exemplo `{nome, idade}` ou `{nome, usuarioId, musicaIds}`, e cada adaptador em `index.html` traduz para o formato do protocolo: JSON, query GraphQL, envelope SOAP ou mensagem protobuf.
- **Funciona com as versões Java e Python**, porque as duas usam o mesmo contrato. Basta apontar para o servidor certo.
- O painel **Última chamada** mostra a requisição e a resposta reais. No gRPC aparecem também os bytes do protobuf. O tempo e o tamanho de cada chamada ficam no **Histórico**, o que ajuda a montar os slides de comparação.

## Rodar tudo de uma vez (para a apresentação)

Na raiz do repositório, com a branch `frontend`:

```powershell
powershell -ExecutionPolicy Bypass -File frontend\rodar-tudo.ps1
```

O script baixa a versão mais recente de cada branch e prepara os ambientes Python. Depois abre cada servidor na sua própria janela e abre o navegador em `http://localhost:3000`. Para parar, feche as janelas. Na página, escolha **Java ou Python** e o protocolo.

|          | REST | GraphQL | SOAP | gRPC  |
|----------|------|---------|------|-------|
| Java     | 9081 | 9082    | 9083 | 9090  |
| Python   | 8001 | 8002    | 8003 | 50051 |

Precisa de Python e Java 17 ou mais recente no PATH. As versões Java levam cerca de 1 minuto para compilar e subir. Opções: `-SemJava` ou `-SemPython`.

## Rodar só o frontend

```bash
cd frontend
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python server.py              # abre em http://localhost:3000
```

Depois suba o serviço que você quer usar. Se ele não estiver na porta da tabela acima, troque o endereço no campo **Servidor** da página.

O botão **Criar dados de exemplo** cadastra 2 usuários, 4 músicas e 3 playlists usando o protocolo selecionado.

## Por que existe o `server.py`

- **CORS:** o navegador bloqueia chamadas da página (porta 3000) para os serviços (porta 8080). O `/proxy` só repassa a requisição que a própria página montou, sem mudar o corpo.
- **gRPC:** o navegador não fala gRPC direto, porque não tem acesso ao HTTP/2 do jeito que o gRPC precisa. O `/grpc/{op}` funciona como ponte: recebe JSON, converte para protobuf pelo `catalogo.proto`, o mesmo da versão Java, chama o servidor e devolve JSON. Em produção, o normal seria usar gRPC-Web com um proxy Envoy.

O `server.py` só aceita chamar serviços em `localhost`.

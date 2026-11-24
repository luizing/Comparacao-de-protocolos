# Trabalho 6: Comparação de Tecnologias de Invocação de Serviços Remotos

Um serviço de streaming de músicas (usuários, músicas e playlists) implementado em **REST, GraphQL, SOAP e gRPC**, nas linguagens **Java** (Spring Boot) e **Python**. Todas as versões usam o mesmo contrato, e um **frontend único** conversa com qualquer uma delas.

## Rodar tudo

1. Instale o **Python 3.10 ou mais recente** (no instalador, marque "Add python.exe to PATH") e o **JDK 17 ou mais recente**.
2. Clone esta branch:
   ```
   git clone -b apresentacao https://github.com/luizing/Compara-o-de-protocolos.git
   ```
3. Dê **dois cliques em `rodar-tudo.bat`**.

O script prepara o ambiente Python, compila as versões Java e abre cada servidor na sua própria janela. Depois abre o navegador em **http://localhost:3000**. Na página, escolha **Java ou Python**, o protocolo, e clique em **Criar dados de exemplo**.

- **Na primeira vez** o Maven e o pip baixam as dependências. Precisa de internet e leva alguns minutos.
- **Nas próximas vezes** sobe em segundos, porque não recompila. Para forçar a compilação: `rodar-tudo.bat -Recompilar`.
- **Para parar**, feche as janelas dos servidores. Os dados ficam em memória e zeram a cada execução.
- Opções: `-SemJava` (só Python) e `-SemPython` (só Java).

## Portas

|          | REST | GraphQL | SOAP | gRPC  |
|----------|------|---------|------|-------|
| Java     | 9081 | 9082    | 9083 | 9090  |
| Python   | 8001 | 8002    | 8003 | 50051 |

Frontend: http://localhost:3000

## Estrutura

```
java/rest      Spring Boot, REST (/api/...)
java/graphql   Spring Boot, GraphQL (/graphql)
java/soap      Spring Boot, SOAP (/ws, streaming.xsd)
java/grpc      Spring Boot, gRPC (catalogo.proto)
python/rest    FastAPI
python/graphql Strawberry + FastAPI
python/soap    FastAPI + lxml (mesmo contrato do streaming.xsd)
python/grpc    grpcio (mesmo catalogo.proto)
frontend/      página única + server.py (proxy por causa do CORS e ponte gRPC)
rodar-tudo.bat / rodar-tudo.ps1
```

Cada pasta tem um README com o passo a passo para rodar só aquela versão.

Esta branch junta, em pastas, o código das branches `main` (REST), `graphql`, `soap`, `grpc`, `python-*` e `frontend`. O desenvolvimento continua nessas branches.

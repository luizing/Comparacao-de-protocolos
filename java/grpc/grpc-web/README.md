# Ponte gRPC-Web

O navegador não acessa gRPC nativo diretamente. Este proxy Envoy recebe chamadas
gRPC-Web em `http://localhost:8081` e as encaminha ao servidor gRPC da aplicação,
que deve estar disponível em `localhost:9090`.

Em um terminal, inicie a aplicação Spring Boot (ela serve o frontend em `8080` e
o serviço gRPC nativo em `9090`):

```bash
./mvnw spring-boot:run
```

Em outro terminal, inicie a ponte na pasta `demo`:

```bash
docker compose -f compose.grpc-web.yaml up
```

Depois, abra `http://localhost:8080`. Para encerrar a ponte, use `Ctrl+C` ou
`docker compose -f compose.grpc-web.yaml down`.

## Erro `package CatalogoGrpc does not exist`

`CatalogoGrpc` é gerada automaticamente pelo Maven a partir de
`src/main/proto/catalogo.proto`. Execute a geração antes de compilar:

```bash
./mvnw clean generate-sources
./mvnw spring-boot:run
```

Na IDE, recarregue o projeto como um projeto Maven depois de abrir ou trocar de
branch. A classe gerada ficará em
`target/generated-sources/protobuf/grpc-java/com/example/demo/grpc/`.

package com.example.demo.grpc;

import io.grpc.Server;
import io.grpc.netty.shaded.io.grpc.netty.NettyServerBuilder;
import java.io.IOException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class GrpcServerConfiguration {

    @Bean(destroyMethod = "shutdown")
    Server grpcServer(CatalogoGrpcService catalogoGrpcService, @Value("${grpc.server.port:9090}") int port) throws IOException {
        return NettyServerBuilder.forPort(port).addService(catalogoGrpcService).build().start();
    }
}

FROM alpine:3.19

RUN apk add --no-cache \
    musl-dev \
    gcc \
    make \
    openssl-dev \
    openssl-libs-static \
    zlib-dev \
    ca-certificates

WORKDIR /app

# Copy source and build
COPY proxy.c .
COPY Makefile .

RUN make

# Certs are volume-mounted at runtime (see docker-compose)
# server.pem and ca.pem are bind-mounted from ./proxy/

EXPOSE 443

ENTRYPOINT ["./tls_proxy"]

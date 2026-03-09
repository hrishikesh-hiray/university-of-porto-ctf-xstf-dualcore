# Stage 1: Proxy builder
FROM alpine:3.19 AS proxy-builder
RUN apk add --no-cache musl-dev gcc make openssl-dev openssl-libs-static zlib-dev
WORKDIR /build
COPY proxy/proxy.c .
COPY proxy/Makefile .
RUN make

# Stage 2: Final image
FROM python:3.11-alpine

# Install dependencies
RUN apk add --no-cache supervisor gcc musl-dev openssl-dev libffi-dev

# 1. Create dedicated users and a shared group
RUN addgroup -S appgroup && \
    adduser -S public-user -G appgroup && \
    adduser -S admin-user -G appgroup && \
    adduser -S proxy-user -G appgroup

# 2. Setup Directories
WORKDIR /app
RUN mkdir -p /app/public-app /app/admin-app /app/proxy /app/certs /tmp/shared-logs

# ---- public-app ----
COPY public-app/requirements.txt /app/public-app/
RUN pip install --no-cache-dir -r /app/public-app/requirements.txt
COPY public-app/app.py /app/public-app/
COPY public-app/flag.txt /app/public-app/
COPY public-app/template /app/public-app/template
RUN touch /tmp/app.log && chmod 666 /tmp/app.log

# ---- admin-app ----
COPY admin-app/requirements.txt /app/admin-app/
RUN pip install --no-cache-dir -r /app/admin-app/requirements.txt
COPY admin-app/app.py /app/admin-app/
RUN mkdir -p /app/admin-app/uploads

# ---- proxy ----
COPY --from=proxy-builder /build/tls_proxy /app/proxy/
COPY proxy/server.pem /app/proxy/
COPY proxy/ca.pem /app/proxy/

RUN chown -R public-user:appgroup /app/public-app && chmod 700 /app/public-app
RUN chmod 400 /app/public-app/flag.txt

RUN chown -R admin-user:appgroup /app/admin-app && chmod 700 /app/admin-app

# Proxy needs the certs
RUN chown -R proxy-user:appgroup /app/proxy /app/certs && chmod 700 /app/proxy /app/certs

# Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 443

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

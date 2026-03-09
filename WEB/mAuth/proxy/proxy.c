#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509.h>
#include <openssl/pem.h>
#include <openssl/bio.h>
#include <time.h>

static char *PUBLIC_APP_HOST;
static char *PUBLIC_APP_PORT;
static char *ADMIN_APP_HOST;
static char *ADMIN_APP_PORT;
static char *CERT_STORE_PATH;

#define LISTEN_PORT 443
#define BUF_SIZE    65536

typedef struct {
    char sni[256];
    int  client_authed;
    int  has_secret_extension;
} conn_state_t;

static int sni_callback(SSL *ssl, int *al, void *arg) {
    (void)al;
    (void)arg;

    const char *sni = SSL_get_servername(ssl, TLSEXT_NAMETYPE_host_name);
    conn_state_t *state = (conn_state_t *)SSL_get_app_data(ssl);

    if (sni && state) {
        strncpy(state->sni, sni, sizeof(state->sni) - 1);
        state->sni[sizeof(state->sni) - 1] = '\0';
        printf("[SNI] captured: %s\n", state->sni);
    }

    return SSL_TLSEXT_ERR_OK;
}

static int validate_client_cert_against_file(SSL *ssl) {
    char path[512];
    snprintf(path, sizeof(path), "%s/admin.cert", CERT_STORE_PATH);

    FILE *f = fopen(path, "r");
    if (!f) {
        printf("[CERT] Cannot open %s — no cert\n", path);
        return 0;
    }
    fseek(f, 0, SEEK_END);
    long disk_len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *disk_pem = malloc(disk_len + 1);
    if (!disk_pem) { fclose(f); return 0; }
    fread(disk_pem, 1, disk_len, f);
    fclose(f);
    disk_pem[disk_len] = '\0';

    X509 *client_cert = SSL_get1_peer_certificate(ssl);

    if (!client_cert) {
        printf("[CERT] Client presented no certificate\n");
        free(disk_pem);
        return 0;
    }

    BIO *bio = BIO_new(BIO_s_mem());
    if (!bio) { X509_free(client_cert); free(disk_pem); return 0; }
    PEM_write_bio_X509(bio, client_cert);
    X509_free(client_cert);

    char client_pem[8192];
    int client_len = BIO_read(bio, client_pem, sizeof(client_pem) - 1);
    BIO_free(bio);
    if (client_len <= 0) { free(disk_pem); return 0; }
    client_pem[client_len] = '\0';

    int match = (strlen(client_pem) == (size_t)disk_len && memcmp(client_pem, disk_pem, disk_len) == 0);

    printf("[CERT] Validation result: %s\n", match ? "PASS" : "FAIL");
    free(disk_pem);
    return match;
}

static void info_callback(const SSL *ssl, int where, int ret) {
    (void)ret;

    if (!(where & SSL_CB_HANDSHAKE_DONE))
        return;

    conn_state_t *state = (conn_state_t *)SSL_get_app_data(ssl);
    if (!state)
        return;

    if (!state->client_authed) {
        state->client_authed = validate_client_cert_against_file((SSL *)ssl);
        if (state->client_authed) {
            printf("[RENEGO] Client authenticated after renegotiation\n");
        }
    }
}


static int check_access(conn_state_t *state) {
    if (!state->has_secret_extension) {
        printf("[ACCESS] DENIED — Missing secret ALPN protocol\n");
        return 0;
    }

    if (strcmp(state->sni, "admin.challenge.com") == 0) {
        if (!state->client_authed) {
            printf("[ACCESS] DENIED — SNI=admin but not authenticated\n");
            return 0;
        }
        return 1;
    }

    if (strcmp(state->sni, "challenge.com") == 0) {
      printf("[ACCESS] ALLOWED — SNI=%s, authed=%d\n", state->sni, state->client_authed);
      return 1;
    }

    return 0;
}


static int parse_host_header(const char *http, char *out, size_t outlen) {
    const char *p = strstr(http, "Host:");
    if (!p) p = strstr(http, "host:");
    if (!p) return 0;

    p += 5;
    while (*p == ' ') p++;

    size_t i = 0;
    while (*p && *p != '\r' && *p != '\n' && i < outlen - 1) {
        out[i++] = *p++;
    }

    out[i] = '\0';
    return 1;
}

static void generate_random_alpn(char *output, size_t outlen) {
    time_t now = time(NULL);
    time_t window = now / 300;

    srand((unsigned int)window);

    int r1 = rand();
    int r2 = rand();
    int r3 = rand();

    snprintf(output, outlen, "ctf-%08x-%08x-%08x", r1, r2, r3);
}

static int alpn_select_cb(SSL *ssl, const unsigned char **out, unsigned char *outlen, const unsigned char *in, unsigned int inlen, void *arg) {
    (void)arg;
    // Generate current random ALPN
    char secret_alpn[128];
    generate_random_alpn(secret_alpn, sizeof(secret_alpn));
    size_t secret_len = strlen(secret_alpn);

    printf("[ALPN] Expecting: %s\n", secret_alpn);

    for (unsigned int i = 0; i < inlen; ) {
        unsigned char len = in[i];

        if (i + 1 + len > inlen) break;

        if (len == secret_len && memcmp(in + i + 1, secret_alpn, len) == 0) {
            *out = in + i + 1;
            *outlen = len;

            conn_state_t *state = (conn_state_t *)SSL_get_app_data(ssl);
            if (state) {
                state->has_secret_extension = 1;
                printf("[ALPN] Secret protocol matched!\n");
            }
            return SSL_TLSEXT_ERR_OK;
        }

        i += len + 1;
    }

    return SSL_TLSEXT_ERR_NOACK;
}

static ssize_t backend_roundtrip(const char *host, const char *port, const char *request, size_t req_len, char *resp_buf, size_t resp_buflen) {
    struct addrinfo hints = {0}, *res = NULL;
    hints.ai_family   = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    if (getaddrinfo(host, port, &hints, &res) != 0) {
        printf("[FWD] getaddrinfo failed for %s:%s\n", host, port);
        return -1;
    }

    int sock = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    if (sock < 0) { freeaddrinfo(res); return -1; }

    if (connect(sock, res->ai_addr, res->ai_addrlen) != 0) {
        printf("[FWD] connect failed to %s:%s\n", host, port);
        close(sock); freeaddrinfo(res); return -1;
    }
    freeaddrinfo(res);

    send(sock, request, req_len, 0);

    ssize_t total = 0, n;
    while ((n = recv(sock, resp_buf + total, resp_buflen - total, 0)) > 0) {
        total += n;
        if ((size_t)total >= resp_buflen) break;
    }
    close(sock);
    return total;
}

static void remove_auth_header(char *buf, size_t *len) {
    char *pos = buf;
    char *end = buf + *len;

    while (pos < end) {
        char *line_start = pos;
        char *line_end = strstr(pos, "\r\n");
        if (!line_end) break;

        if ((line_end - line_start >= 22) &&
            (strncasecmp(line_start, "X-Proxy-Authenticated:", 22) == 0)) {
            size_t line_len = (line_end + 2) - line_start;  // Include \r\n
            size_t remaining = end - (line_end + 2);

            memmove(line_start, line_end + 2, remaining);
            *len -= line_len;
            end -= line_len;

        } else {
            pos = line_end + 2;
        }
    }
}

static void handle_connection(int client_fd, SSL_CTX *ctx) {
    SSL *ssl = SSL_new(ctx);
    if (!ssl) { close(client_fd); return; }

    conn_state_t state = {0};
    SSL_set_app_data(ssl, &state);

    SSL_set_fd(ssl, client_fd);
    SSL_set_accept_state(ssl);      /* We are the server side */

    if (SSL_do_handshake(ssl) != 1) {
        printf("[TLS] Handshake failed: ");
        ERR_print_errors_fp(stderr);
        SSL_free(ssl);
        close(client_fd);
        return;
    }

    printf("[TLS] Handshake complete. SNI=%s\n", state.sni);

    if (!check_access(&state)) {
        const char *deny = "HTTP/1.1 403 Forbidden\r\n"
                           "Content-Length: 9\r\n\r\nForbidden";
        SSL_write(ssl, deny, strlen(deny));
        SSL_shutdown(ssl);
        SSL_free(ssl);
        close(client_fd);
        return;
    }

    char req_buf[BUF_SIZE];
    int  req_len = SSL_read(ssl, req_buf, sizeof(req_buf) - 1);

    size_t req_len_size = (size_t)req_len;
    remove_auth_header(req_buf, &req_len_size);
    req_len = (int)req_len_size;

    if (req_len <= 0) {
        printf("[TLS] Failed to read HTTP request\n");
        SSL_shutdown(ssl); SSL_free(ssl); close(client_fd);
        return;
    }
    req_buf[req_len] = '\0';

    char host_header[256] = {0};
    if (!parse_host_header(req_buf, host_header, sizeof(host_header))) {
        strcpy(host_header, state.sni);  /* fallback to SNI */
    }

    printf("[HTTP] Host header: %s\n", host_header);

    const char *backend_host;
    const char *backend_port;

    if (strcmp(host_header, "admin.challenge.com") == 0) {
        backend_host = ADMIN_APP_HOST;
        backend_port = ADMIN_APP_PORT;
        printf("[ROUTE] → admin-app\n");
    } else {
        backend_host = PUBLIC_APP_HOST;
        backend_port = PUBLIC_APP_PORT;
        printf("[ROUTE] → public-app\n");
    }

    char fwd_buf[BUF_SIZE];
    size_t fwd_len = 0;

    if (state.client_authed) {
        const char *eol = strstr(req_buf, "\r\n");
        if (eol) {
            size_t first_line_len = (eol - req_buf) + 2;
            memcpy(fwd_buf, req_buf, first_line_len);
            fwd_len = first_line_len;

            const char *auth_hdr = "X-Proxy-Authenticated: true\r\n";
            memcpy(fwd_buf + fwd_len, auth_hdr, strlen(auth_hdr));
            fwd_len += strlen(auth_hdr);

            memcpy(fwd_buf + fwd_len, eol + 2, req_len - first_line_len);
            fwd_len += req_len - first_line_len;
        } else {
            memcpy(fwd_buf, req_buf, req_len);
            fwd_len = req_len;
        }
    } else {
        memcpy(fwd_buf, req_buf, req_len);
        fwd_len = req_len;
    }

    char resp_buf[BUF_SIZE];
    ssize_t resp_len = backend_roundtrip(backend_host, backend_port,
                                          fwd_buf, fwd_len,
                                          resp_buf, sizeof(resp_buf));
    if (resp_len > 0) {
        SSL_write(ssl, resp_buf, resp_len);
    }

    SSL_shutdown(ssl);
    SSL_free(ssl);
    close(client_fd);
}

static int verify_always_ok(int preverify_ok, X509_STORE_CTX *ctx) {
    (void)preverify_ok;
    (void)ctx;
    return 1;   /* Accept everything at the TLS layer */
}

int main(void) {
    PUBLIC_APP_HOST = getenv("PUBLIC_APP_HOST") ?: "public-app";
    PUBLIC_APP_PORT = getenv("PUBLIC_APP_PORT") ?: "5000";
    ADMIN_APP_HOST  = getenv("ADMIN_APP_HOST")  ?: "admin-app";
    ADMIN_APP_PORT  = getenv("ADMIN_APP_PORT")  ?: "5001";
    CERT_STORE_PATH = getenv("CERT_STORE_PATH") ?: "certs";

    printf("[PROXY] Starting on port %d\n", LISTEN_PORT);
    printf("[PROXY] Public backend:  %s:%s\n", PUBLIC_APP_HOST, PUBLIC_APP_PORT);
    printf("[PROXY] Admin backend:   %s:%s\n", ADMIN_APP_HOST,  ADMIN_APP_PORT);
    printf("[PROXY] Cert store:      %s\n",    CERT_STORE_PATH);

    /* ── SSL context ── */
    SSL_CTX *ctx = SSL_CTX_new(TLS_server_method());
    if (!ctx) { perror("SSL_CTX_new"); return 1; }

    SSL_CTX_set_min_proto_version(ctx, TLS1_2_VERSION);
    SSL_CTX_clear_options(ctx, SSL_OP_NO_RENEGOTIATION);

    /* Load server certificate and key */
    if (SSL_CTX_use_certificate_chain_file(ctx, "server.pem") != 1) {
        ERR_print_errors_fp(stderr);
        printf("[PROXY] Failed to load server cert\n");
        SSL_CTX_free(ctx); return 1;
    }
    if (SSL_CTX_use_PrivateKey_file(ctx, "server.pem", SSL_FILETYPE_PEM) != 1) {
        ERR_print_errors_fp(stderr);
        printf("[PROXY] Failed to load server key\n");
        SSL_CTX_free(ctx); return 1;
    }

    SSL_CTX_set_verify(ctx, SSL_VERIFY_PEER, verify_always_ok);
    SSL_CTX_set_tlsext_servername_callback(ctx, sni_callback);
    SSL_CTX_set_info_callback(ctx, info_callback);
    SSL_CTX_set_alpn_select_cb(ctx, alpn_select_cb, NULL);

    int listenfd = socket(AF_INET, SOCK_STREAM, 0);
    if (listenfd < 0) { perror("socket"); return 1; }

    int opt = 1;
    setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr = {0};
    addr.sin_family      = AF_INET;
    addr.sin_port        = htons(LISTEN_PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(listenfd, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        perror("bind"); return 1;
    }
    listen(listenfd, 128);
    printf("[PROXY] Listening on 0.0.0.0:%d\n", LISTEN_PORT);

    while (1) {
        int client_fd = accept(listenfd, NULL, NULL);
        if (client_fd < 0) {
            perror("accept");
            continue;
        }
        printf("[PROXY] New connection accepted (fd=%d)\n", client_fd);

        pid_t pid = fork();
        if (pid == 0) {
          close(listenfd);
          handle_connection(client_fd, ctx);
          exit(0);
        } else if (pid > 0) {
          close(client_fd);
          } else {
            perror("fork");
        }
        handle_connection(client_fd, ctx);
    }

    SSL_CTX_free(ctx);
    close(listenfd);
    return 0;
}

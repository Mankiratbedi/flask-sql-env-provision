/*
 * Minimal TCP key-value server for binary protocol.
 * Protocol: magic "PTC0" (4 bytes), opcode (1 byte), key_len (2 bytes BE), key; for SET: value_len (2 BE), value.
 * Response: magic "PTC0", 0x03 (RESP), value_len (2 BE), value.
 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdint.h>

#define MAGIC "PTC0"
#define OP_SET 0x01
#define OP_GET 0x02
#define OP_RESP 0x03
#define PORT 9999
#define MAX_KEY 256
#define MAX_VAL 4096

static char store_key[MAX_KEY];
static char store_val[MAX_VAL];
static int store_set = 0;

static int read_exact(int fd, void *buf, size_t n) {
    char *p = (char *)buf;
    while (n) {
        ssize_t r = read(fd, p, n);
        if (r <= 0) return -1;
        p += r;
        n -= (size_t)r;
    }
    return 0;
}

static int write_exact(int fd, const void *buf, size_t n) {
    const char *p = (const char *)buf;
    while (n) {
        ssize_t w = write(fd, p, n);
        if (w <= 0) return -1;
        p += w;
        n -= (size_t)w;
    }
    return 0;
}

static void handle_connection(int client_fd) {
    char magic[4];
    unsigned char opcode;
    uint16_t key_len, val_len;
    char key_buf[MAX_KEY], val_buf[MAX_VAL];

    while (1) {
        if (read_exact(client_fd, magic, 4) != 0) break;
        if (memcmp(magic, MAGIC, 4) != 0) break;
        if (read_exact(client_fd, &opcode, 1) != 0) break;
        if (read_exact(client_fd, &key_len, 2) != 0) break;
        key_len = ntohs(key_len);
        if (key_len > MAX_KEY - 1) break;
        if (read_exact(client_fd, key_buf, key_len) != 0) break;
        key_buf[key_len] = '\0';

        if (opcode == OP_SET) {
            if (read_exact(client_fd, &val_len, 2) != 0) break;
            val_len = ntohs(val_len);
            if (val_len > MAX_VAL - 1) break;
            if (read_exact(client_fd, val_buf, val_len) != 0) break;
            val_buf[val_len] = '\0';
            strncpy(store_key, key_buf, MAX_KEY - 1);
            store_key[MAX_KEY - 1] = '\0';
            strncpy(store_val, val_buf, MAX_VAL - 1);
            store_val[MAX_VAL - 1] = '\0';
            store_set = 1;
            /* Response: empty value for SET ack */
            if (write_exact(client_fd, MAGIC, 4) != 0) break;
            opcode = OP_RESP;
            if (write_exact(client_fd, &opcode, 1) != 0) break;
            key_len = 0;
            if (write_exact(client_fd, &key_len, 2) != 0) break;
        } else if (opcode == OP_GET) {
            if (write_exact(client_fd, MAGIC, 4) != 0) break;
            opcode = OP_RESP;
            if (write_exact(client_fd, &opcode, 1) != 0) break;
            if (store_set && strcmp(store_key, key_buf) == 0) {
                val_len = (uint16_t)strlen(store_val);
                uint16_t val_len_be = htons(val_len);
                if (write_exact(client_fd, &val_len_be, 2) != 0) break;
                if (write_exact(client_fd, store_val, val_len) != 0) break;
            } else {
                uint16_t zero_be = htons(0);
                if (write_exact(client_fd, &zero_be, 2) != 0) break;
            }
        } else {
            break;
        }
    }
}

int main(void) {
    int server_fd, client_fd;
    struct sockaddr_in addr;
    socklen_t len = sizeof(addr);

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        return 1;
    }
    int one = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one)) < 0) {
        perror("setsockopt");
        return 1;
    }
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(PORT);
    if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        return 1;
    }
    if (listen(server_fd, 1) < 0) {
        perror("listen");
        return 1;
    }
    client_fd = accept(server_fd, (struct sockaddr *)&addr, &len);
    if (client_fd < 0) {
        perror("accept");
        return 1;
    }
    handle_connection(client_fd);
    close(client_fd);
    close(server_fd);
    return 0;
}

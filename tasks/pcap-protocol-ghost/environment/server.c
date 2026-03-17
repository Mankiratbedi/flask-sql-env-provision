#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <time.h>
#include <fcntl.h>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <errno.h>

#define PORT 9999
#define MAGIC "\xCA\xFE\xBA\xBE"
#define MAGIC_LEN 4
#define OP_HELLO      0x01
#define OP_CHALLENGE  0x02
#define OP_AUTH       0x03
#define OP_AUTH_OK    0x04
#define OP_AUTH_FAIL  0x05
#define OP_FETCH      0x10
#define OP_FETCH_RESP 0x11
#define OP_NOT_FOUND  0x12

static char auth_key[256];
static int auth_key_len = 0;
static const char *SECRET_FLAG = "GHOST-7a3b9c2d-e5f1-4a8b-b2c3-d4e5f6a7b8c9";

static void load_auth_key(void) {
    FILE *f = fopen("/app/auth_key.txt", "r");
    if (!f) { perror("open auth_key.txt"); exit(1); }
    if (fgets(auth_key, sizeof(auth_key), f) == NULL) { fclose(f); exit(1); }
    fclose(f);
    auth_key_len = strlen(auth_key);
    while (auth_key_len > 0 && (auth_key[auth_key_len-1] == '\n' || auth_key[auth_key_len-1] == '\r'))
        auth_key[--auth_key_len] = '\0';
}

static int recv_all(int fd, uint8_t *buf, int len) {
    int got = 0;
    while (got < len) {
        int r = recv(fd, buf + got, len - got, 0);
        if (r <= 0) return -1;
        got += r;
    }
    return got;
}

static int send_frame(int fd, uint8_t opcode, const uint8_t *payload, uint16_t plen) {
    uint8_t hdr[7];
    memcpy(hdr, MAGIC, 4);
    hdr[4] = opcode;
    hdr[5] = (plen >> 8) & 0xFF;
    hdr[6] = plen & 0xFF;
    if (send(fd, hdr, 7, 0) != 7) return -1;
    if (plen > 0 && send(fd, payload, plen, 0) != (ssize_t)plen) return -1;
    return 0;
}

static int recv_frame(int fd, uint8_t *opcode, uint8_t *payload, uint16_t *plen) {
    uint8_t hdr[7];
    if (recv_all(fd, hdr, 7) < 0) return -1;
    if (memcmp(hdr, MAGIC, 4) != 0) return -1;
    *opcode = hdr[4];
    *plen = ((uint16_t)hdr[5] << 8) | hdr[6];
    if (*plen > 0 && recv_all(fd, payload, *plen) < 0) return -1;
    return 0;
}

static void handle_client(int cfd) {
    uint8_t opcode;
    uint8_t payload[4096];
    uint16_t plen;

    /* Expect HELLO */
    if (recv_frame(cfd, &opcode, payload, &plen) < 0 || opcode != OP_HELLO) goto done;

    /* Send CHALLENGE with random nonce */
    uint8_t nonce[16];
    int urnd = open("/dev/urandom", O_RDONLY);
    if (urnd < 0 || read(urnd, nonce, 16) != 16) goto done;
    if (urnd >= 0) close(urnd);
    if (send_frame(cfd, OP_CHALLENGE, nonce, 16) < 0) goto done;

    /* Expect AUTH */
    if (recv_frame(cfd, &opcode, payload, &plen) < 0 || opcode != OP_AUTH) goto done;

    /* Verify HMAC-SHA256(key, nonce)[:16] */
    uint8_t expected[32];
    unsigned int md_len = 32;
    HMAC(EVP_sha256(), auth_key, auth_key_len, nonce, 16, expected, &md_len);

    if (plen < 16 || memcmp(payload, expected, 16) != 0) {
        send_frame(cfd, OP_AUTH_FAIL, (uint8_t*)"bad auth", 8);
        goto done;
    }
    if (send_frame(cfd, OP_AUTH_OK, NULL, 0) < 0) goto done;

    /* Handle FETCH requests */
    while (1) {
        if (recv_frame(cfd, &opcode, payload, &plen) < 0) break;
        if (opcode != OP_FETCH) break;
        payload[plen] = '\0';
        if (strcmp((char*)payload, "secret") == 0) {
            send_frame(cfd, OP_FETCH_RESP, (uint8_t*)SECRET_FLAG, (uint16_t)strlen(SECRET_FLAG));
        } else {
            send_frame(cfd, OP_NOT_FOUND, payload, plen);
        }
    }
done:
    close(cfd);
}

int main(void) {
    load_auth_key();
    int sfd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;
    bind(sfd, (struct sockaddr*)&addr, sizeof(addr));
    listen(sfd, 5);
    while (1) {
        int cfd = accept(sfd, NULL, NULL);
        if (cfd >= 0) handle_client(cfd);
    }
    return 0;
}

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

static uint32_t custom_hash(const uint8_t *data, size_t len) {
    uint32_t h = 0xDEADBEEFu;
    for (size_t i = 0; i < len; i++) {
        h ^= (uint32_t)data[i];
        h = ((h << 7) | (h >> 25));
        h *= 0x45D9F3Bu;
    }
    return h ^ (h >> 16);
}

static int hex_decode(const char *hex, uint8_t *out, size_t *outlen) {
    size_t hlen = strlen(hex);
    if (hlen % 2 != 0) return -1;
    for (size_t i = 0; i < hlen; i += 2) {
        if (!isxdigit((unsigned char)hex[i]) || !isxdigit((unsigned char)hex[i+1]))
            return -1;
        unsigned int byte;
        sscanf(hex + i, "%02x", &byte);
        out[i / 2] = (uint8_t)byte;
    }
    *outlen = hlen / 2;
    return 0;
}

int main(void) {
    char hex[8192];
    if (fgets(hex, sizeof(hex), stdin) == NULL) {
        hex[0] = '\0';
    }
    size_t n = strlen(hex);
    while (n > 0 && (hex[n-1] == '\n' || hex[n-1] == '\r' || hex[n-1] == ' '))
        hex[--n] = '\0';

    uint8_t buf[4096];
    size_t blen = 0;
    if (n > 0 && hex_decode(hex, buf, &blen) < 0) {
        fprintf(stderr, "invalid hex input\n");
        return 1;
    }

    printf("%u\n", custom_hash(buf, blen));
    return 0;
}

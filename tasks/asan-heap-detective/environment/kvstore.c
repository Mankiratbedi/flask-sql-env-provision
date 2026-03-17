#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TABLE_SIZE 64

typedef struct Node {
    char key[64];
    char value[256];
    struct Node *next;
} Node;

static Node *table[TABLE_SIZE];
static Node *last_accessed = NULL;  /* LRU-style access cache — BUG: not invalidated on delete */

static unsigned int hash_key(const char *key) {
    unsigned int h = 5381;
    while (*key) h = ((h << 5) + h) ^ (unsigned char)*key++;
    return h % TABLE_SIZE;
}

static Node *lookup(const char *key) {
    /* BUG: Check dangling cache first without verifying the node is still alive */
    if (last_accessed != NULL && strcmp(last_accessed->key, key) == 0) {
        return last_accessed;  /* heap-use-after-free if node was deleted */
    }
    unsigned int idx = hash_key(key);
    Node *cur = table[idx];
    while (cur) {
        if (strcmp(cur->key, key) == 0) {
            last_accessed = cur;
            return cur;
        }
        cur = cur->next;
    }
    return NULL;
}

static void cmd_set(const char *key, const char *value) {
    unsigned int idx = hash_key(key);
    Node *cur = table[idx];
    while (cur) {
        if (strcmp(cur->key, key) == 0) {
            strncpy(cur->value, value, 255);
            cur->value[255] = '\0';
            last_accessed = cur;
            return;
        }
        cur = cur->next;
    }
    Node *n = malloc(sizeof(Node));
    if (!n) { perror("malloc"); exit(1); }
    strncpy(n->key, key, 63);
    n->key[63] = '\0';
    strncpy(n->value, value, 255);
    n->value[255] = '\0';
    n->next = table[idx];
    table[idx] = n;
    last_accessed = n;
}

static void cmd_get(const char *key) {
    Node *n = lookup(key);
    if (n) {
        printf("%s=%s\n", key, n->value);
    } else {
        printf("%s=NOT_FOUND\n", key);
    }
}

static void cmd_delete(const char *key) {
    unsigned int idx = hash_key(key);
    Node **pp = &table[idx];
    while (*pp) {
        if (strcmp((*pp)->key, key) == 0) {
            Node *dead = *pp;
            *pp = dead->next;
            /* BUG: last_accessed is NOT cleared even if it points to the freed node */
            free(dead);
            return;
        }
        pp = &(*pp)->next;
    }
}

int main(void) {
    char line[400];
    while (fgets(line, sizeof(line), stdin)) {
        line[strcspn(line, "\n")] = '\0';
        if (strncmp(line, "SET ", 4) == 0) {
            char *sp = strchr(line + 4, ' ');
            if (sp) { *sp = '\0'; cmd_set(line + 4, sp + 1); }
        } else if (strncmp(line, "GET ", 4) == 0) {
            cmd_get(line + 4);
        } else if (strncmp(line, "DELETE ", 7) == 0) {
            cmd_delete(line + 7);
        }
    }
    return 0;
}

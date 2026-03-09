#include <stdio.h>
#include <stdlib.h>

int main(void) {
    FILE *fptr;
    char flag[256];

    fptr = fopen("/flag.txt", "r");

    if (fptr == NULL) {
        perror("Error opening file /flag.txt");
        return 1;
    }

    if (fgets(flag, sizeof(flag), fptr) != NULL) {
        printf(flag);
    } else {
        printf("File is empty.\n");
    }

    fclose(fptr);
    return 0;
}


#include <stdio.h>
#include <unistd.h>

int main() {
    for (int i = 0; i < 2048; i++) {
        printf("Running for %d seconds\n", i);
        sleep(1);
    }

    printf("Complete!");
    return 0;
}
CC      = gcc
CFLAGS  = -Wall -Wextra -g -I/usr/include
LDFLAGS = -lssl -lcrypto

TARGET  = tls_proxy
SRC     = proxy.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET)

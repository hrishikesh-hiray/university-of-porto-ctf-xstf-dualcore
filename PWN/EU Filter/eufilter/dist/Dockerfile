FROM ubuntu:24.04

# Use DEBIAN_FRONTEND=noninteractive to skip timezone prompts during install
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    qemu-user \
    busybox-static \
    libc6-mips-cross \
    && rm -rf /var/lib/apt/lists/*

# Setup the application directory
COPY www/ /www/
RUN chmod +x /www/cgi-bin/eufilter.bin /www/cgi-bin/eufilter.cgi

# Copy and setup entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# QEMU environment variable for MIPS emulation
ENV QEMU_LD_PREFIX=/usr/mips-linux-gnu

EXPOSE 4006

# Use the absolute path for the entrypoint to be safe
CMD ["/entrypoint.sh"]

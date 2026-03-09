#!/bin/sh
L=$(wc -c < /tmp/write_test.bin)
cat /tmp/write_test.bin | REQUEST_METHOD=POST QUERY_STRING="url=discord.com" CONTENT_TYPE="multipart/form-data; boundary=----x" CONTENT_LENGTH=$L qemu-mips -strace /www/cgi-bin/eufilter.bin > /tmp/q_out.txt 2> /tmp/q_err.txt
EC=$?
echo $EC > /tmp/q_ec.txt

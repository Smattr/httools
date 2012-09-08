#!/bin/bash

# Generates a .htpasswd file for Apache by amalgamating users' personal
# .htpasswd files. Note, we use grep to make sure a user can't use their own
# .htpasswd to set someone else's password.

if [ $# -ne 1 ]; then
    echo "Usage: $0 output_filename" >&2
    exit 1
fi

for u in `cut -d":" -f1 /etc/passwd`; do
    if [ -f "/home/$u/.htpasswd" ]; then
        grep "^$u:" "/home/$u/.htpasswd"
    fi
done >$1

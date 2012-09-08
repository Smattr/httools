#!/bin/bash

# Generates a .htgroups file for Apache .htaccesses to reference, such that the
# .htaccess groups match the system groups.

if [ $# -ne 1 ]; then
    echo "Usage: $0 output_file" >&2
    exit 1
fi

sed -e 's/\(.*\):.*:.*:\(.*\)/\1: \2/' -e 's/,/ /g' /etc/group >$1

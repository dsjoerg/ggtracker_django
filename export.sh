#!/bin/bash
if [ ! "$1" ]; then
    echo "ENV_FILE is a required argument."
    echo "USAGE: source export.sh ENV_FILE";
else
    `sed -ne 's/\([A-Z].*\)/export \1/p' <$1`
fi

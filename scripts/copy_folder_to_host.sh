#!/usr/bin/env bash

echo "options:"
echo "\$1: container folder we copy from"
echo "\$2: container folder we copy to (could also be an host folder)"

cp -r "$1" "$2"
echo "copied folder $1 to folder $2!"
ls -ld "$2"
ls -l "$2"

exit 0
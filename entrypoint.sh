#!/bin/sh -l

if [ "$7" = "true" ]; then
    python /upload_package.py $1 /github/workspace/$2 $3 $4 $5 $6 --auto-update --profile-name "$8" --package-name "$9"
else
    python /upload_package.py $1 /github/workspace/$2 $3 $4 $5 $6
fi

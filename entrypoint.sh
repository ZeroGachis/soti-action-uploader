#!/bin/sh -l

echo "TEST  $1 $2/artifact/$3 $4 $5 $6 $7"
./python upload_package.py $1 $2/artifact/$3 $4 $5 $6 $7

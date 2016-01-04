#!/bin/bash -x
set -e
top=$(pwd)
rm -fr out || /bin/true
mkdir -p out
zip out/deploy.zip func.py
cd venv/lib/python2.7/site-packages 
zip ${top}/out/deploy.zip -x boto* -r .

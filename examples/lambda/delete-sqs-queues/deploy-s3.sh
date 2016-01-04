#!/bin/bash -x
if [[ ! -n "${BUCKET}" ]]; then
  echo set BUCKET env var
  exit 2
fi
name=$(basename $(pwd))
ls -lh out/deploy.zip
aws s3 cp --acl public-read out/deploy.zip s3://${BUCKET}/${name}/latest.zip

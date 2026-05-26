#!/bin/zsh

set -e

SCRIPT_DIR=$(readlink -f ${0%/*}/)
cd $SCRIPT_DIR/..

print -P "%F{yellow}Updating auth for docker registry...%f"

if [[ -n "$CI_AWS_SECRET_ACCESS_KEY" ]]; then
  print -P "%F{yellow}Using credentials from CI environment.%f"
  export AWS_ACCESS_KEY_ID=$CI_AWS_ACCESS_KEY_ID
  export AWS_SECRET_ACCESS_KEY=$CI_AWS_SECRET_ACCESS_KEY
  export AWS_REGION=us-east-2
fi

aws_pass=$(aws ecr get-login-password --region us-east-2)
echo $aws_pass | docker login --username AWS --password-stdin 402590802363.dkr.ecr.us-east-2.amazonaws.com &>/dev/null

print -P "%F{yellow}done.%f\n"

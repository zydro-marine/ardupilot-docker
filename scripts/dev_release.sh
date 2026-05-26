#!/usr/bin/env zsh

set -e

SCRIPT_DIR=$(readlink -f ${0%/*}/)
cd $SCRIPT_DIR/..

architecture=""
case $(uname -m) in
    x86_64)  architecture="x86_64" ;;
    aarch64) architecture="aarch64" ;;
    arm*)    architecture="aarch64" ;;
esac

./scripts/dev_aws_auth.sh

export dry_run=0
export docker=0
export target_release_stage="dev"

version_str=$(python3 ./scripts/detect-version-tag.py)
git_sha=$(git rev-parse --short HEAD)
version_combined="$version_str-$git_sha"
export target_version="$version_combined"

for i in "$@"
do
case $i in
    --docker) docker=1 ;;
    --dry-run) dry_run=1 ;;
    --release) target_release_stage=prod ;;
    *) ;;
esac
done

if [ "$target_release_stage" = "prod" ]; then
    export version_combined="$version_str"
fi

if [ "$dry_run" = "1" ]; then
    print -P "%F{yellow}Dry run. exiting early%f\n"
    exit 0
fi

if [ "$docker" = "1" ]; then
    print -P "%F{yellow}Pushing release ardupilot-docker:$version_str-$git_sha-$architecture to ECR...%f\n"

    docker tag 402590802363.dkr.ecr.us-east-2.amazonaws.com/ardupilot-docker:latest-$git_sha-$architecture 402590802363.dkr.ecr.us-east-2.amazonaws.com/ardupilot-docker:$version_str-$git_sha-$architecture
    docker push 402590802363.dkr.ecr.us-east-2.amazonaws.com/ardupilot-docker:$version_str-$git_sha-$architecture
fi

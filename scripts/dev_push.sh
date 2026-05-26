#!/bin/zsh

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

git_sha=$(git rev-parse --short HEAD)

has_param() {
    local term="$1"
    shift
    for arg; do
        if [[ $arg == "$term" ]]; then
            return 0
        fi
    done
    return 1
}

if has_param "--docker" "$@"; then
    ./scripts/dev_aws_auth.sh

    print -P "%F{yellow}pushing ardupilot-docker ($architecture $git_sha)...%f\n"

    docker push 402590802363.dkr.ecr.us-east-2.amazonaws.com/ardupilot-docker:latest-$git_sha-$architecture

    docker tag 402590802363.dkr.ecr.us-east-2.amazonaws.com/ardupilot-docker:latest-$git_sha-$architecture 402590802363.dkr.ecr.us-east-2.amazonaws.com/ardupilot-docker:latest-$architecture
    docker push 402590802363.dkr.ecr.us-east-2.amazonaws.com/ardupilot-docker:latest-$architecture
fi

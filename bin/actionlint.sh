#!/usr/bin/env bash

SHELLCHECK_OPTS="-e SC2086"

export BASEDIR=$(cd $(dirname $0)/..; pwd)
docker run --rm -e SHELLCHECK_OPTS="${SHELLCHECK_OPTS}" -v ${BASEDIR}:/repo --workdir /repo rhysd/actionlint:latest -color

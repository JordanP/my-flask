#!/usr/bin/env bash
set -euo pipefail

DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

print_help () {
    echo "Usage: deploy.sh [OPTIONS]"
    echo "Options:"
    echo "  -h              Print help"
    echo "  -p GCP-PROJECT  Set GCP project                (REQUIRED)"
    echo "  -t TAG          Set deployed image's tag       (defaults to current tag or commit id)"
    echo "  -l              Local Docker image build"
    echo "  --debug         Print generated yaml conf"
    echo "  --dry-run       Don't execute deployment"
}

print_conf() {
    find tools/kube/ -type f -exec bash -c 'echo -e "---\n$(cat {} | envsubst)"' \;
}

deploy_kubernetes() {
    echo "[.] Deploying ${IMAGE}:${TAG} on K8s  ..."
    kubectl --context stag-dashboard apply -f <(print_conf)
}

build_and_push_docker() {
    docker build --rm=false -f Dockerfile -t ${IMAGE}:${TAG} .
    ${DOCKER_CMD} push ${IMAGE}:${TAG}
}

default_tag() {
    local tag=`git describe --exact-match HEAD 2> /dev/null`
    if [ -z "$tag" ]; then tag=$(git rev-parse HEAD); fi
    echo ${tag}
}

check_image_exists() {
    local image_tag="${IMAGE}:${TAG}"
    local verify_tag="${image_tag}-build-successful"
    if ! ${DOCKER_CMD} pull "$verify_tag" > /dev/null 2>&1; then
        echo '[!] The control image "'${verify_tag}'" was not found in the registry'
        exit 1
    fi
}

TAG=`default_tag`
DRY_RUN=false
DEBUG=false
LOCAL_BUILD=false

argument_parse () {
    SHORTOPTS="t:p:lh"
    LONGOPTS="dry-run,debug"
    ARGS=$(getopt -s bash --options $SHORTOPTS \
        --longoptions $LONGOPTS --name "$(basename "$0")" -- "$@")
    eval set -- "$ARGS"
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                ;;
            --debug)
                DEBUG=true
                ;;
            -t)
                TAG=$2
                shift
                ;;
            -p)
                GCP_PROJECT=$2
                shift
                ;;
            -l)
                LOCAL_BUILD=true
                ;;
            -h)
                print_help
                exit 0
                ;;
            --)
                shift
                break
                ;;
             *)
                shift
                break
                ;;
        esac
        shift
    done
}

if [ $# -eq 0 ]; then print_help; exit 0; fi
argument_parse ${@}

if [[ $GCP_PROJECT == "" ]]; then
  echo "-p argument is required"
  exit 1
fi

DOCKER_CMD="gcloud --project ${GCP_PROJECT} docker --"
IMAGE="eu.gcr.io/${GCP_PROJECT}/${PWD##*/}"

export IMAGE TAG

if [ "$DEBUG" = true ] ; then
    print_conf
fi

if [[ ${LOCAL_BUILD} == true ]]; then
  build_and_push_docker
else
  check_image_exists
fi

if [[ "$DRY_RUN" != true ]] ; then
    deploy_kubernetes
fi

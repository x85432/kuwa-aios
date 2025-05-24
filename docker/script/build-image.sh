#!/bin/bash
set -e

function cleanup {
    popd >/dev/null
}

pushd $(dirname "$0") > /dev/null
trap cleanup EXIT

if command -v nvidia-smi &>/dev/null; then
    image_variant=cu121
else
    image_variant=cpu
fi
image_variant=${1:-$image_variant}
shift

if [ "$image_variant" == "cu121" ]; then
    base_image=nvidia/cuda:12.1.1-runtime-ubuntu22.04
else
    base_image=ubuntu:22.04
fi

echo -e "building docker image. IMAGE_VARIANT=${image_variant}; BASE_IMAGE=${base_image}"
cd ..
./run.sh build --build-arg IMAGE_VARIANT=${image_variant} --build-arg BASE_IMAGE=${base_image} $@
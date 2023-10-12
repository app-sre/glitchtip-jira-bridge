#!/bin/bash
set -ev

test -z "$NO_PUSH" && docker login -u="$QUAY_USER" -p="$QUAY_TOKEN" quay.io

make_image() {
    IMG_NAME="$1"
    DOCKERFILE="$2"
    TARGET="$3"

    QUAY_IMAGE="quay.io/app-sre/$IMG_NAME"
    IMG="$IMG_NAME:latest"
    if [ -n "$GIT_COMMIT" ]; then
        GIT_HASH=${GIT_COMMIT:0:7}
    fi

    # Build Image
    echo "Building $IMG_NAME with $DOCKERFILE ..."
    set -x
    docker build . -f "$DOCKERFILE" --target "$TARGET" -t "$IMG"

    # Tag and push the image
    docker tag "$IMG" "$QUAY_IMAGE:latest"
    test -z "$NO_PUSH" && docker push "$QUAY_IMAGE:latest"
    if [ -n "$GIT_HASH" ]; then
        docker tag "$IMG" "$QUAY_IMAGE:$GIT_HASH"
        test -z "$NO_PUSH" && docker push "$QUAY_IMAGE:$GIT_HASH"
    fi
    set +x
}

make_image "${IMAGE_NAME:-glitchtip-jira-bridge}" "Dockerfile" "${TARGET:-release}"

exit 0

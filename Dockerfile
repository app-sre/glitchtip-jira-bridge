FROM registry.access.redhat.com/ubi9/python-312@sha256:1d8846b7c6558a50b434f1ea76131f200dcdd92cfaf16b81996003b14657b491 AS base
COPY LICENSE /licenses/


#
# Builder image
#
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.5.13@sha256:926f32f1722d6a9187f5a48fe0da68c34cab9512885e1857219a3fe0a546ab0d /uv /bin/uv

ENV \
    # use venv from ubi image
    UV_PROJECT_ENVIRONMENT="$APP_ROOT" \
    # compile bytecode for faster startup
    UV_COMPILE_BYTECODE="true" \
    # disable uv cache. it doesn't make sense in a container
    UV_NO_CACHE=true

COPY pyproject.toml uv.lock ./
# Test lock file is up to date
RUN uv lock --locked
# Install the project dependencies
RUN uv sync --frozen --no-install-project --no-group dev

COPY README.md app.sh ./
COPY glitchtip_jira_bridge ./glitchtip_jira_bridge
RUN uv sync --frozen --no-group dev



#
# Test image
#
FROM builder AS test

COPY Makefile ./
RUN uv sync --frozen

COPY tests ./tests
RUN make test


#
# Production image
#
FROM base AS prod
COPY --from=builder /opt/app-root /opt/app-root
ENTRYPOINT [ "./app.sh" ]

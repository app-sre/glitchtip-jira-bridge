FROM registry.access.redhat.com/ubi9/python-312@sha256:fc9702e64d88c030b19b2298a5b6604bd2a5ac9f210833691cdaac3a43e29a2d AS base
COPY LICENSE /licenses/


#
# Builder image
#
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.8.10@sha256:b05b3d61eb2b264ed785265b71155738a0d3d382ea0699e048d4b36f90b88788 /uv /bin/uv

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

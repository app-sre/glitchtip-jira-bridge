FROM registry.access.redhat.com/ubi9/python-312@sha256:0c23550f08fb257342be41d1784af37906f9aee8aae8a577fb83e6b41d1d5e0c AS base
COPY LICENSE /licenses/


#
# Builder image
#
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.6.9@sha256:cbc016e49b55190e17bfd0b89a1fdc1a54e0a54a8f737dfacc72eca9ad078338 /uv /bin/uv

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

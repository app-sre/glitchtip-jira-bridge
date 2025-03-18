FROM registry.access.redhat.com/ubi9/python-312@sha256:b3316249c58e1800118ec1f311514f6ec355a60d8c78383bfa868887952b2ee1 AS base
COPY LICENSE /licenses/


#
# Builder image
#
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.6.7@sha256:d25a9b42ecc3aac0d63782654dcb2ab4b304f86357794b05a5c39b17f4777339 /uv /bin/uv

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

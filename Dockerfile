FROM registry.access.redhat.com/ubi9/python-312@sha256:88ea2d10c741f169681102b46b16c66d20c94c3cc561edbb6444b0de3a1c81b3 AS base
COPY LICENSE /licenses/


#
# Builder image
#
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.5.7@sha256:23272999edd22e78195509ea3fe380e7632ab39a4c69a340bedaba7555abe20a /uv /bin/uv

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

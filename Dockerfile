FROM registry.access.redhat.com/ubi10/python-314-minimal@sha256:0d6de003c233849fc6690277d18b66a2f0217b6c8c447c074462aa22267b6982 AS base
COPY LICENSE /licenses/
ENV \
    # use venv from ubi image
    UV_PROJECT_ENVIRONMENT="$APP_ROOT" \
    # compile bytecode for faster startup
    UV_COMPILE_BYTECODE="true" \
    # disable uv cache. it doesn't make sense in a container
    UV_NO_CACHE=true \
    IS_TESTED_FLAG="/tmp/is_tested"


#
# Builder image
#
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.11.25@sha256:1e3808aa9023d0980e7c15b1fa7c1ac16ff35925780cf5c459858b2d693f01a9 /uv /bin/uv

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
FROM base AS test
COPY --from=ghcr.io/astral-sh/uv:0.11.25@sha256:1e3808aa9023d0980e7c15b1fa7c1ac16ff35925780cf5c459858b2d693f01a9 /uv /bin/uv

COPY --from=builder $APP_ROOT $APP_ROOT

USER 0
# Install base dependencies
RUN microdnf install -y make && microdnf clean all
USER 1001

COPY Makefile ./
RUN uv sync --frozen

COPY tests ./tests
RUN make test
RUN touch ${IS_TESTED_FLAG}

#
# Production image
#
FROM base AS prod
COPY --from=builder $APP_ROOT $APP_ROOT
COPY --from=test ${IS_TESTED_FLAG} ${IS_TESTED_FLAG}

ENTRYPOINT [ "./app.sh" ]

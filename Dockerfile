FROM registry.access.redhat.com/ubi9/ubi-minimal:9.4 as base-python
ENV PYTHONUNBUFFERED=1 \
    PATH="/code/.venv/bin:$PATH"

RUN microdnf upgrade -y && \
    microdnf install -y \
        shadow-utils \
        python3.11 && \
    microdnf clean all && \
    update-alternatives --install /usr/bin/python3 python /usr/bin/python3.11 1 && \
    ln -snf /usr/bin/python3.11 /usr/bin/python && \
    python3 -m ensurepip && \
    pip3 install -U pip setuptools wheel poetry

COPY LICENSE /licenses/
WORKDIR /code
RUN useradd -u 5000 app && chown -R app:app /code

# ---- Interims image to get and build all the python dependencies ----
FROM base-python as build-base-python
ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# install the dependencies
RUN microdnf install -y \
        libcurl-devel \
        openssl-devel \
        gcc \
        python3.11-devel

# required for poetry to install the dependencies
COPY --chown=app:app pyproject.toml poetry.lock README.md /code/
# the code
COPY --chown=app:app glitchtip_jira_bridge /code/glitchtip_jira_bridge/
COPY --chown=app:app app.sh /code/

# install the python dependencies
RUN poetry install --no-interaction --no-ansi --only main

# ---- Bundle everything together in the final image ----
FROM base-python as release
EXPOSE 8080

RUN microdnf install -y \
    libcurl-minimal \
    && microdnf clean all

COPY --from=build-base-python /code/ /code/
USER app:app
CMD ["/code/app.sh"]

# ---- Test image ----
FROM build-base-python as test-image
# install the test dependencies
RUN poetry install --no-interaction --no-ansi
# install the tests
COPY --chown=app:app tests /code/tests/
COPY --chown=app:app Makefile /code/
USER app:app

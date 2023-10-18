#!/bin/bash
if [[ "${GJB_DEBUG}" == "1" ]]; then
    set -x
fi

if [ -r "settings.conf" ]; then
    set -a
    # shellcheck source=/dev/null
    . settings.conf
    set +a
fi

START_MODE="${GJB_START_MODE:-web}"
APP_PORT="${GJB_APP_PORT:-8080}"
UVICORN_OPTS="${GJB_UVICORN_OPTS:- --host 0.0.0.0}"
UVICORN_OPTS="${UVICORN_OPTS} --port ${APP_PORT}"
# start celery worker with solo pool by default to ensure only one worker is running
# we scale the number of workers using kubernetes pods
# this also ensures prometheus metrics are working
CELERY_OPTS="${GJB_CELERY_OPTS:- --loglevel=info --pool solo}"

if [ -n "${GJB_DEBUG}" ]; then
    UVICORN_OPTS="${UVICORN_OPTS} --log-level debug --reload"
fi
if [[ "${START_MODE}" == "web" ]]; then
    echo "---> Serving application with uvicorn ..."
    # shellcheck disable=SC2086
    exec uvicorn $UVICORN_OPTS "$@" glitchtip_jira_bridge.main:app
elif [[ "${START_MODE}" == "worker" ]]; then
    echo "---> Starting worker ..."
    # shellcheck disable=SC2086
    exec celery --app=glitchtip_jira_bridge.worker worker ${CELERY_OPTS} "$@"
else
    echo "unknow mode $START_MODE - use 'web' or 'worker' instead"
fi

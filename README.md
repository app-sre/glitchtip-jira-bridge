# glitchtip-jira-bridge
The Glitchtip-Jira-Bridge seamlessly processes Glitchtip alerts through webhooks, transforming them into detailed, actionable Jira tickets.

# Configuration

All configuration is done through environment variables.

The following table lists the available environment variables for the FastAPI web application:

| Environment variable | Description                                                                                                           | Default value                |
| -------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| GJB_START_MODE       | Start mode for the application (web or worker)                                                                        | `web`                        |
| GJB_UVICORN_OPTS     | Uvicorn options for the web application                                                                               | `--host 0.0.0.0 --port 8080` |
| GJB_DEBUG            | Enable debug logging (`0 = false; 1 = true`)                                                                          | `0`                          |
| GJB_ROOT_PATH        | Root path for the application                                                                                         | `/`                          |
| GJB_API_KEYS         | List of API keys that are allowed to access the application (JSON string list); See [Authentication](#authentication) |                              |

The available [Celery](https://docs.celeryq.dev/en/stable/index.html) worker options:

| Environment variable             | Description                         | Default value                 |
| -------------------------------- | ----------------------------------- | ----------------------------- |
| GJB_CELERY_OPTS                  | Celery worker daemon options        | `--loglevel=info --pool solo` |
| GJB_BROKER_URL                   | Celery broker URL                   | local SQS                     |
| GJB_SQS_URL                      | Celery SQS queue URL                | local SQS                     |
| GJB_BROKER_AWS_REGION            | Celery broker AWS region            | `us-east-1`                   |
| GJB_BROKER_AWS_ACCESS_KEY_ID     | Celery broker AWS access key ID     | `localstack`                  |
| GJB_BROKER_AWS_SECRET_ACCESS_KEY | Celery broker AWS secret access key | `localstack`                  |
| GJB_RETRIES                      | Max celery task retries             | `3`                           |
| GJB_RETRY_DELAY                  | Celery task retry delay             | `60`                          |

The Jira client configuration:
| Environment variable | Description  | Default value                     |
| -------------------- | ------------ | --------------------------------- |
| GJB_JIRA_API_URL     | Jira URL     | `https://issues.stage.redhat.com` |
| GJB_JIRA_API_KEY     | Jira API key |                                   |

Cache configuration:

| Environment variable               | Description                    | Default value  |
| ---------------------------------- | ------------------------------ | -------------- |
| GJB_DYNAMODB_URL                   | DynamoDB URL                   | local DynamoDB |
| GJB_DYNAMODB_TABLE                 | DynamoDB table name            | `gjb-cache`    |
| GJB_DYNAMODB_AWS_REGION            | DynamoDB region                | `us-east-1`    |
| GJB_DYNAMODB_AWS_ACCESS_KEY_ID     | DynamoDB AWS access key ID     | `localstack`   |
| GJB_DYNAMODB_AWS_SECRET_ACCESS_KEY | DynamoDB AWS secret access key | `localstack`   |
| GJB_CACHE_TTL                      | Cache TTL in seconds           | `7200`         |


> [!WARNING]
>
> **DynamoDB** is the only supported cache backend at the moment.

# Authentication

The application supports API key authentication. The key is passed as `Authentication` HTTP header (`Authentication: Bearer XXX`) or via `token` query parameter (`?token=XXX`).

# Development

## Prepare your dev environment

Create a virtual environment for the project:

```bash
$ poetry install
```

### MacOS and PyCurl

If you are using MacOS, you may need to install PyCurl with OpenSSL support. This can be done with the following command:

```bash
$ brew install openssl curl
$ brew info curl
...
For compilers to find curl you may need to set:
  export LDFLAGS="-L/usr/local/opt/curl/lib"
  export CPPFLAGS="-I/usr/local/opt/curl/include"

For pkg-config to find curl you may need to set:
  export PKG_CONFIG_PATH="/usr/local/opt/curl/lib/pkgconfig"
...

$ export LDFLAGS="-L/usr/local/opt/curl/lib"
$ export CPPFLAGS="-I/usr/local/opt/curl/include"
$ export PKG_CONFIG_PATH="/usr/local/opt/curl/lib/pkgconfig"
$ export PYCURL_SSL_LIBRARY=openssl
$ pip uninstall pycurl
$ pip install --no-cache-dir pycurl
```
## Local configuration

Get a personal access token from [staging Jira](https://issues.stage.redhat.com) and add it to a local `src/settings.conf` file:

```bash
$ cat src/settings.conf
export GJB_JIRA_API_KEY="<YOUR PERSONAL STAGING JIRA ACCESS TOKEN>"
export HTTPS_PROXY=squid.corp.redhat.com:3128
export GJB_DEBUG=1
```


## Localstack

Start a local AWS environment with the following command:

```bash
$ docker compose up localstack
```

## Glitchtip Jira Bridge Web and Worker

Start the web part of the application in one terminal:

```bash
$ cd src
$ GJB_START_MODE=web ./app.sh
```

And a celery worker in another terminal:

```bash
$ cd src
$ GJB_START_MODE=worker ./app.sh
```

# Con-PCA API #

[![GitHub Build Status](https://github.com/cisagov/con-pca-api/workflows/build/badge.svg)](https://github.com/cisagov/con-pca-api/actions/workflows/build.yml)
[![CodeQL](https://github.com/cisagov/con-pca-api/workflows/CodeQL/badge.svg)](https://github.com/cisagov/con-pca-api/actions/workflows/codeql-analysis.yml)
[![Known Vulnerabilities](https://snyk.io/test/github/cisagov/con-pca-api/badge.svg)](https://snyk.io/test/github/cisagov/con-pca-api)

Required for install:

<!--Please add required software information here-->

This is a Docker skeleton project that can be used to quickly get a
new [cisagov](https://github.com/cisagov) GitHub Docker project
started.  This skeleton project contains [licensing
information](LICENSE), as well as [pre-commit hooks](https://pre-commit.com)
and [GitHub Actions](https://github.com/features/actions) configurations
appropriate for Docker containers and the major languages that we use.

## Running ##

### Running with Docker ###

To run the `cisagov/con-pca-api` image via Docker:

```console
docker run cisagov/con-pca-api:0.0.1
```

### Running with Docker Compose ###

1. Create a `docker-compose.yml` file similar to the one below to use [Docker Compose](https://docs.docker.com/compose/).

    ```yaml
    ---
    version: "3.7"

    services:
      api:
        image: cisagov/con-pca-api:0.0.1
        volumes:
          - type: bind
            source: <your_log_dir>
            target: /var/log
        environment:
          - ECHO_MESSAGE="Hello from docker compose"
        ports:
          - target: 8080
            published: 8080
            protocol: tcp
    ```

1. Start the container and detach:

    ```console
    docker compose up --detach
    ```

## Using secrets with your container ##

This container also supports passing sensitive values via [Docker
secrets](https://docs.docker.com/engine/swarm/secrets/).  Passing sensitive
values like your credentials can be more secure using secrets than using
environment variables.  See the
[secrets](#secrets) section below for a table of all supported secret files.

1. To use secrets, create a `quote.txt` file containing the values you want set:

    ```text
    Better lock it in your pocket.
    ```

1. Then add the secret to your `docker-compose.yml` file:

    ```yaml
    ---
    version: "3.7"

    secrets:
      quote_txt:
        file: quote.txt

    services:
      api:
        image: cisagov/con-pca-api:0.0.1
        volumes:
          - type: bind
            source: <your_log_dir>
            target: /var/log
        environment:
          - ECHO_MESSAGE="Hello from docker compose"
        ports:
          - target: 8080
            published: 8080
            protocol: tcp
        secrets:
          - source: quote_txt
            target: quote.txt
    ```

## Updating your container ##

### Docker Compose ###

1. Pull the new image from Docker Hub:

    ```console
    docker compose pull
    ```

1. Recreate the running container by following the [previous instructions](#running-with-docker-compose):

    ```console
    docker compose up --detach
    ```

### Docker ###

1. Stop the running container:

    ```console
    docker stop <container_id>
    ```

1. Pull the new image:

    ```console
    docker pull cisagov/con-pca-api:0.0.1
    ```

1. Recreate and run the container by following the [previous instructions](#running-with-docker).

## Image tags ##

The images of this container are tagged with [semantic
versions](https://semver.org) of the underlying con-pca-api project that they
containerize.  It is recommended that most users use a version tag (e.g.
`:0.0.1`).

| Image:tag | Description |
|-----------|-------------|
|`cisagov/con-pca-api:1.2.3`| An exact release version. |
|`cisagov/con-pca-api:1.2`| The most recent release matching the major and minor version numbers. |
|`cisagov/con-pca-api:1`| The most recent release matching the major version number. |
|`cisagov/con-pca-api:edge` | The most recent image built from a merge into the `develop` branch of this repository. |
|`cisagov/con-pca-api:nightly` | A nightly build of the `develop` branch of this repository. |
|`cisagov/con-pca-api:latest`| The most recent release image pushed to a container registry.  Pulling an image using the `:latest` tag [should be avoided.](https://vsupalov.com/docker-latest-tag/) |

See the [tags tab](https://hub.docker.com/r/cisagov/con-pca-api/tags) on Docker
Hub for a list of all the supported tags.

```shell
git clone git@github.com:cisagov/con-pca-api.git
cd con-pca-api/
```

| Mount point | Purpose        |
|-------------|----------------|
| `/var/log`  |  Log storage   |

## Ports ##

The following ports are exposed by this container:

| Port | Purpose        |
|------|----------------|
| 5000 | Flask API Port |
| 8000 | Flask Click/Opens Tracking Port |
| 27017 | MongoDB |

The [Docker composition](docker-compose.yml) publishes the
exposed ports at 5000 and 8000.

## Environment variables ##

All environment defaults can be found in the [default environment file](etc/env.dist).
Once copied to the base directory as `.env`, they will automatically be included
in docker-compose.

### Required ###

There are no required environment variables.

| Name  | Purpose | Default |
|-------|---------|---------|
| `FLASK_APP` | Flask app to use. | `api.main:app` |
| `FLASK_ENV` | Flask environment. | `development` |
| `DEBUG` | Setup debug on or off. | `1` |
| `DB_HOST` | Mongo host. | `mongodb` |
| `DB_PORT` | Mongo port. | `27017` |
| `DB_PW` | Mongo password. | `changeme` |
| `DB_USER` | Mongo user. | `changeme` |
| `WORKERS` | Amount of Gunicorn workers if Debug set to 0. | `4` |
| `AWS_ACCESS_KEY_ID` | The AWS access key to access AWS services. | `changeme` |
| `AWS_SECRET_ACCESS_KEY` | The AWS secret access key for access to AWS services. | `changeme` |
| `AWS_DEFAULT_REGION` | The default AWS region. | `us-east-1` |
| `AWS_COGNITO_ENABLED` | Whether to enable authentication via Cognito. | `0` |
| `MONGO_INITDB_ROOT_PASSWORD` | The password to start mongo container with. | `changeme` |
| `MONGO_INITDB_ROOT_USERNAME` | The username to start mongo container with. | `changeme` |
| `MAILGUN_API_KEY` | A private API key linked to the mailgun account managing sending domains. | `changeme` |
| `EMAIL_MINUTES` | How often to check for phishing emails to send. | `1` |
| `TASK_MINUTES` | How often to check for tasks to run. | `1` |
| `FAILED_EMAIL_MINUTES` | How often to check for email events that failed. | `1440` |
| `DELAY_MINUTES` | Time to delay between starting a subscription and sending emails. | `1` |

### Optional ###

| Name  | Purpose | Default |
|-------|---------|---------|
| `AWS_COGNITO_USER_POOL_ID` | The user pool id if using cognito auth.  | |
| `AWS_COGNITO_USER_POOL_CLIENT_ID` | The client id if using cognito auth. | |
| `SES_ASSUME_ROLE_ARN` | The SES role to assume for sending notifications. | |
| `SMTP_FROM` | The from address for notifications. | |
| `MAXMIND_USER_ID` | User ID for using maxmind database for clicks/opens info. | |
| `MAXMIND_LICENSE_KEY` | License key for using maxmind database for clicks/opens info. | |

## Secrets ##

| Filename     | Purpose |
|--------------|---------|
| `quote.txt` | Replaces the secret stored in the con-pca-api library's package data. |

## Building from source ##

Build the image locally using this git repository as the [build context](https://docs.docker.com/engine/reference/commandline/build/#git-repositories):

```console
docker build \
  --build-arg VERSION=0.0.1 \
  --tag cisagov/con-pca-api:0.0.1 \
  https://github.com/cisagov/con-pca-api.git#develop
```

## Cross-platform builds ##

To create images that are compatible with other platforms, you can use the
[`buildx`](https://docs.docker.com/buildx/working-with-buildx/) feature of
Docker:

1. Copy the project to your machine using the `Code` button above
   or the command line:

    ```console
    git clone https://github.com/cisagov/con-pca-api.git
    cd con-pca-api
    ```

1. Create the `Dockerfile-x` file with `buildx` platform support:

    ```console
    ./buildx-dockerfile.sh
    ```

1. Build the image using `buildx`:

    ```console
    docker buildx build \
      --file Dockerfile-x \
      --platform linux/amd64 \
      --build-arg VERSION=0.0.1 \
      --output type=docker \
      --tag cisagov/con-pca-api:0.0.1 .
    ```

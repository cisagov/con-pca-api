.PHONY: all help build logs loc up stop down
include .env
export
ts := $(shell /bin/date "+%Y-%m-%d--%H-%M-%S")

# make all - Default Target. Does nothing.
all:
	@echo "Django helper commands."
	@echo "For more information try 'make help'."

# target: help - Display callable targets.
help:
	@egrep "^# target:" [Mm]akefile

# target: env = copy env vars to your .env file
env:
	cp ./etc/env.dist ./.env

# target: attach = attach to target container
attach:
	docker attach --sig-proxy=false pca-api

# target: build = build all containers
build:
	docker-compose -f new-docker-compose.yml build
build_old:
	docker-compose build

# target: app logs - Runs django logs in the terminal
logs:
	 docker logs pca-api

# target: up - Run local web server.
up:
	docker-compose -f new-docker-compose.yml up -d
up_old:
	docker-compose up -d

# target: stop - Stop all docker containers
stop:
	docker-compose -f new-docker-compose.yml stop
stop_old:
	docker-compose stop

# target: down - Remove all docker containers
down:
	docker-compose -f new-docker-compose.yml down
down_old:
	docker-compose down

# target: redeploy = bring down, rebuild and redeploy all containers
redeploy: down build up

# target: shell - django shell within container
shell:
	docker exec -it pca-api python3

# target: build_emails: build mjml emails - requires: npm install -g mjml
build_emails:
	mjml new/api/templates/emails/mjml/* -o new/api/templates/emails/

# target: dummy - initializes init_dummy_data for cpa
dummy:
	docker exec -it pca-api python scripts/create_dummy_data.py

# target: dummy_reporting initalizes dummy reporting subscriptions
dummy_reporting:
	docker exec -it pca-api python scripts/create_dummy_reporting_data.py

# target: coverage - runs pytests against code and generates coverage html
coverage:
	coverage run --omit *.venv*,*test* -m pytest ./tests/ --disable-warnings
	coverage html

# target: cc - calculates cyclomatic complexity
cc:
	radon cc ./src/ -e "*.venv*" -s -o SCORE

# target: lint = lint all files
lint:
	pre-commit autoupdate
	pre-commit run --all-files

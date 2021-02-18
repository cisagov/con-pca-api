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
	docker-compose build

# target: app logs - Runs django logs in the terminal
logs:
	 docker logs pca-api

# target: up - Run local web server.
up:
	 docker-compose up -d

# target: stop - Stop all docker containers
stop:
	docker-compose stop

# target: down - Remove all docker containers
down:
	docker-compose down

# target: redeploy = bring down, rebuild and redeploy all containers
redeploy: down build up

# target: shell - django shell within container
shell:
	docker exec -it pca-api python manage.py shell

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

# target: debug_ptvsd - run debugger with ptvsd
debug_ptvsd:
	docker exec -it pca-api python -m ptvsd --host 0.0.0.0 --port 5679 scripts/create_dummy_data.py

tasks:
	docker exec -it pca-api python lambda_functions/tasks/

lambda_export:
	docker exec -it pca-api python lambda_functions/export.py

lint:
	pre-commit autoupdate
	pre-commit run --all-files

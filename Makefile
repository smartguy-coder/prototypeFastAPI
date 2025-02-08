DC = docker compose
RUN = ${DC} run --rm
LOGS = docker logs
ENV = --env-file .env
APP_FILE = docker-compose.yaml
STORAGES_FILE = docker_compose.yaml
APP_CONTAINER = master-backend-api

.PHONY: app
app:
	${DC} -f ${APP_FILE} ${ENV} up --build -d

.PHONY: app-down
app-down:
	${DC} -f ${APP_FILE} down

.PHONY: app-shell
app-shell:
	${EXEC} ${APP_CONTAINER} bash

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: app-run
app-run-bash:
	${RUN} ${APP_CONTAINER} bash
PROJECT_NAME := drf_template
COMPOSE := docker compose -p $(PROJECT_NAME)_devcontainer -f .devcontainer/compose.yml

include make/container.mk
include make/database.mk
include make/deployment.mk
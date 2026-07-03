
SERVICE ?= server

ssh:
	$(COMPOSE) exec $(SERVICE) bash

shell:
	$(COMPOSE) exec $(SERVICE) ./django_api/manage.py shell 

logs:
	$(COMPOSE) logs --follow $(SERVICE)

test:
	$(COMPOSE) exec $(SERVICE) python ./django_api/manage.py test 

restart:
	$(COMPOSE) restart $(SERVICE)

up:
	. .config/secret/secrets.source && \
	$(COMPOSE) up server database

npm_build:
	cd react && npx vite build --config vite.config.js



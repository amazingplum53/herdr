STACK ?= prod


deploy:
	. .config/secret/secrets.source && \
	pulumi config set --cwd ./.pulumi/ --stack $(STACK) --secret db:password "$$DB_PASSWORD"; \
	pulumi up --cwd ./.pulumi/ --stack $(STACK) --yes
	

destroy:
	pulumi destroy --cwd ./.pulumi/ --stack $(STACK) --yes


migrate_task:
	STACK=$(STACK) AWS_REGION=eu-west-2 ./.pulumi/migrate_task.sh
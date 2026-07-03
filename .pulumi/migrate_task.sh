#!/usr/bin/env bash
set -euo pipefail


CONFIG=$(pulumi stack output migration_config --cwd ./.pulumi/ --stack "$STACK" --json)

CLUSTER=$(echo "$CONFIG" | jq -r '.cluster')
TASK_DEF=$(echo "$CONFIG" | jq -r '.task_definition')
CONTAINER=$(echo "$CONFIG" | jq -r '.container')
SUBNETS=$(echo "$CONFIG" | jq -r '.subnets | join(",")')
SG=$(echo "$CONFIG" | jq -r '.security_group')

TASK_ARN=$(aws ecs run-task \
  --cluster "$CLUSTER" \
  --launch-type FARGATE \
  --task-definition "$TASK_DEF" \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG],assignPublicIp=DISABLED}" \
  --overrides "{
    \"containerOverrides\": [{
      \"name\": \"$CONTAINER\",
      \"command\": [\"./django_api/manage.py\", \"migrate\", \"--noinput\"]
    }]
  }" \
  --query 'tasks[0].taskArn' \
  --output text)

aws ecs wait tasks-stopped --cluster "$CLUSTER" --tasks "$TASK_ARN"

EXIT_CODE=$(aws ecs describe-tasks \
  --cluster "$CLUSTER" \
  --tasks "$TASK_ARN" \
  --query 'tasks[0].containers[0].exitCode' \
  --output text)

test "$EXIT_CODE" = "0"
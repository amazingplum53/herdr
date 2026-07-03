import pulumi
import pulumi_aws as aws
import pulumi_docker as docker
import json
from pulumi import Output
from typing import List, Dict, Tuple

def task_security_group(
    stage: str,
    project_name: str,
    vpc: aws.ec2.Vpc,
    alb_sg: aws.ec2.SecurityGroup,
) -> aws.ec2.SecurityGroup:

    return aws.ec2.SecurityGroup(
        f"{stage}-task-sg-{project_name}",
        vpc_id=vpc.id,
        description="Tasks - allow 8000 from ALB",
        ingress=[aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp", from_port=8000, to_port=8000, security_groups=[alb_sg.id],
        )],
        egress=[aws.ec2.SecurityGroupEgressArgs(
            protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"],
        )],
    )

def ecs(
    stage: str,
    project_name: str,
    cluster: aws.ecs.Cluster,
    vpc: aws.ec2.Vpc,
    subnets: List[Output[str]],
    target_group: aws.lb.TargetGroup,
    image: docker.Image,
    alb_sg: aws.ec2.SecurityGroup,
    task_security_group: aws.ec2.SecurityGroup,
    db_host_name: Output[str]
) -> Tuple[aws.iam.Role, aws.ecs.TaskDefinition, aws.ecs.Service, str]:
    """
    Registers an ECS Task Definition & Fargate Service running `image`
    behind the given ALB target_group.
    """

    log_group = aws.cloudwatch.LogGroup(
        f"{stage}-lg-{project_name}",
        retention_in_days=14,     
    )

    security_group = vpc.default_security_group_id

    # 1) Task execution IAM Role
    task_execution_role = aws.iam.Role(
        f"{stage}-exec-role-{project_name}",
        assume_role_policy=aws.iam.get_policy_document(
            statements=[{
                "actions":   ["sts:AssumeRole"],
                "principals":[{"type":"Service","identifiers":["ecs-tasks.amazonaws.com"]}],
                "effect":    "Allow",
            }]
        ).json,
    )

    aws.iam.RolePolicyAttachment(
        f"{stage}-exec-attach-{project_name}",
        role=task_execution_role.name,
        policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
    )

    # 2) Build container_definitions JSON once 'image' resolves
    container_name = f"{stage}-server-{project_name}"
    all_inputs = Output.all(
        image.repo_digest,
        log_group.name,
        db_host_name,
    )
    container_defs = all_inputs.apply(lambda args: json.dumps([{
        "name":          container_name,
        "image":         args[0],
        "portMappings":  [{"containerPort": 8000}],
        "essential":     True,
        "environment":   [
            { "name": "STACK", "value": stage },
            {"name":"DB_HOST","value": args[2]}
        ],
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": args[1],
                "awslogs-region": aws.config.region,
                "awslogs-stream-prefix": "ecs"
            }
        }
    }]))

    # 3) Task Definition
    task_def = aws.ecs.TaskDefinition(
        f"{stage}-task-def-{project_name}",
        family                   = f"{stage}-{project_name}",
        cpu                      = "512",
        memory                   = "1024",
        network_mode             = "awsvpc",
        requires_compatibilities = ["FARGATE"],
        execution_role_arn       = task_execution_role.arn,
        container_definitions    = container_defs,
    )

    # 4) Fargate Service
    container_service = aws.ecs.Service(
        f"{stage}-service-{project_name}",
        cluster               = cluster.arn,
        task_definition       = task_def.arn,
        desired_count         = 1,
        launch_type           = "FARGATE",
        force_new_deployment  = True,
        network_configuration = aws.ecs.ServiceNetworkConfigurationArgs(
            assign_public_ip = False,
            subnets          = subnets,
            security_groups  = [task_security_group.id],
        ),
        load_balancers=[aws.ecs.ServiceLoadBalancerArgs(
            target_group_arn = target_group.arn,
            container_name   = container_name,
            container_port   = 8000,
        )],
        opts=pulumi.ResourceOptions(depends_on=[task_def]),
        health_check_grace_period_seconds = 120,
    )

    return (
        task_execution_role,
        task_def,
        container_service,
        container_name
    )


def ecr(
    stage: str,
    project_name: str,
    project_path: str,
    image_tag: str = "latest",
) -> Tuple[aws.ecr.Repository, pulumi.Output[str]]:
    """
    Creates (or references) an ECR repo, applies a simple lifecycle policy,
    then builds & pushes your local Docker context to it.
    Returns (repo, image_uri).
    """

    # 1) ECR repository
    repo = aws.ecr.Repository(
        f"{stage}-{project_name}",
        name=f"{stage}-{project_name}",
        image_scanning_configuration=aws.ecr.RepositoryImageScanningConfigurationArgs(
            scan_on_push=True,
        ),
        force_delete=True,
        tags={
            "Environment": stage,
            "Name":        f"{stage}-{project_name}",
        },
    )

    # 2) Keep only last 10 images
    aws.ecr.LifecyclePolicy(
        f"{stage}-{project_name}-lifecycle",
        repository=repo.name,
        policy=json.dumps({
            "rules": [{
                "rulePriority": 1,
                "description": "Keep only last 10 images",
                "selection": {
                    "tagStatus":   "any",
                    "countType":   "imageCountMoreThan",
                    "countNumber": 10,
                },
                "action": {"type": "expire"},
            }]
        }),
    )

    # 3) Auth for Docker → ECR
    auth = aws.ecr.get_authorization_token()

    image = docker.Image(
        f"{stage}-{project_name}-image".replace("_", "-"),
        image_name = repo.repository_url.apply(lambda url: f"{url}:{image_tag}"),
        build = {                       # ← plain Python dict
            "context"   : project_path,
            "dockerfile": project_path + ".devcontainer/server.dockerfile",
        },
        registry   = {
            "server"  : repo.repository_url,
            "username": auth.user_name,
            "password": auth.password,
        },
    )

    # 5) Return repo + fully-qualified URI
    return (repo, image)
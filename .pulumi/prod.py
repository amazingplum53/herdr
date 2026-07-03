"""An AWS Python Pulumi program"""

import pulumi_aws as aws
from infrastructure import static, network, service
from infrastructure.database import aurora_serverless_v2 as database
import pulumi 

def deploy(stage: str, project_name: str):

    PROJECT_ROOT = f"/workspace/{project_name}/"

    VPC, PUBLIC_SUBNETS, PRIVATE_SUBNETS = network.vpc(stage, project_name)

    PUBLIC_SUBNET_IDS = [s.id for s in PUBLIC_SUBNETS]
    PRIVATE_SUBNET_IDS = [s.id for s in PRIVATE_SUBNETS]

    CERTIFICATE_ARN = network.cdn_certificate(stage, project_name)

    BUCKET = static.bucket(stage, project_name)

    CDN = static.cdn(
        stage,
        project_name,
        BUCKET,
        network.DOMAIN_NAME,
        CERTIFICATE_ARN,
    )

    static.allow_cloudfront_access(stage, project_name, BUCKET, CDN)

    network.cdn_alias_record(stage, project_name, CDN)

    ALB, TARGET_GROUP, LISTENER, SG_GROUP = network.alb(stage, project_name, PUBLIC_SUBNET_IDS)

    network.alb_alias_record(stage, project_name, ALB)

    CLUSTER = aws.ecs.Cluster(f"{stage}-cluster-{project_name}") 

    TASK_SECURITY_GROUP = service.task_security_group(
        stage,
        project_name,
        VPC,
        SG_GROUP,
    )

    DB_CLUSTER, DB_WRITER = database(
        stage,
        project_name,
        VPC,
        PRIVATE_SUBNET_IDS,
        allowed_security_group_ids = [TASK_SECURITY_GROUP.id],
    )

    ECR, IMAGE = service.ecr(stage, project_name, PROJECT_ROOT)

    TASK_EXE_ROLE, TASK_DEF, CONTAINER_SERVICE, CONTAINER_NAME = service.ecs(
        stage, 
        project_name,
        CLUSTER, 
        VPC,
        PRIVATE_SUBNET_IDS, 
        TARGET_GROUP, 
        IMAGE,
        SG_GROUP,
        TASK_SECURITY_GROUP,
        DB_CLUSTER.endpoint,
    )

    pulumi.export("migration_config", {
        "cluster": CLUSTER.name,
        "task_definition": TASK_DEF.arn,
        "container": CONTAINER_NAME,
        "subnets": PRIVATE_SUBNET_IDS,
        "security_group": TASK_SECURITY_GROUP.id,
    })


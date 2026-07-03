# database.py
import json
import pulumi
import pulumi_aws as aws
import os
import ast
from pulumi import Output, Input
from typing import List, Optional, Tuple

def aurora_serverless_v2(
    stage: str,
    project_name: str,
    vpc: aws.ec2.Vpc,
    private_subnet_ids: List[Input[str]],
    allowed_security_group_ids: Optional[List[Input[str]]] = [],
    engine: str = "aurora-postgresql",
    engine_version: Optional[str] = None,
    min_acu: float = 0.5,
    max_acu: float = 1.0,
) -> Tuple[aws.rds.Cluster, aws.rds.ClusterInstance]:
    """
    Creates Aurora Serverless v2
    """
    
    cfg = pulumi.Config("db")

    DATABASE = ast.literal_eval(os.environ["DATABASE"])

    password = cfg.get_secret("password")

    subnet_group = aws.rds.SubnetGroup(
        f"{stage}-db-subnets-{project_name}",
        subnet_ids=private_subnet_ids,
    )

    db_sg = aws.ec2.SecurityGroup(
        f"{stage}-db-sg-{project_name}",
        vpc_id=vpc.id,
        description="Aurora Serverless v2 access",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=DATABASE["PORT"],
                to_port=DATABASE["PORT"],
                security_groups=allowed_security_group_ids,
            )
        ] if allowed_security_group_ids else [],
        egress=[aws.ec2.SecurityGroupEgressArgs(
            protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"],
        )],
    )

    cluster = aws.rds.Cluster(
        f"{stage}-aurora-{project_name}",
        engine=engine,
        engine_version=engine_version,
        database_name=DATABASE["NAME"],
        master_username=DATABASE["USERNAME"],
        master_password=password,
        db_subnet_group_name=subnet_group.name,
        vpc_security_group_ids=[db_sg.id],
        port=DATABASE["PORT"],
        serverlessv2_scaling_configuration=aws.rds.ClusterServerlessv2ScalingConfigurationArgs(
            min_capacity=min_acu,
            max_capacity=max_acu,
        ),
        deletion_protection=False,
        skip_final_snapshot=True,
        backup_retention_period=1,
        apply_immediately=True,
    )

    writer = aws.rds.ClusterInstance(
        f"{stage}-aurora-writer-{project_name}",
        cluster_identifier=cluster.id,
        instance_class="db.serverless",
        engine=cluster.engine,
        engine_version=cluster.engine_version,
        publicly_accessible=False,
        db_subnet_group_name=subnet_group.name,
    )

    return cluster, writer

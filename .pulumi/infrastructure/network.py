import pulumi_aws as aws
import pulumi

DOMAIN_NAME = "matthewhill.click"


def vpc(stage, project_name):
    azs = aws.get_availability_zones()

    vpc = aws.ec2.Vpc(
        f"{stage}-vpc-{project_name}",
        cidr_block="10.0.0.0/16",
        enable_dns_hostnames=True,
        enable_dns_support=True,
        tags={"Name": "pulumi-two-az-vpc"},
    )

    # Internet Gateway
    igw = aws.ec2.InternetGateway(
        f"{stage}-igw-{project_name}",
        vpc_id=vpc.id,
        tags={"Name": "pulumi-vpc-igw"},
    )

    # Public route table → IGW
    public_rt = aws.ec2.RouteTable(
        f"{stage}-publicRT-{project_name}",
        vpc_id=vpc.id,
        routes=[aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id,
        )],
        tags={"Name": "pulumi-public-rt"},
    )

    # Public subnets (A/B)
    public_subnet_a = aws.ec2.Subnet(
        f"{stage}-publicSubnetA-{project_name}",
        vpc_id=vpc.id,
        cidr_block="10.0.1.0/24",
        availability_zone=azs.names[0],
        map_public_ip_on_launch=True,
        tags={"Name": pulumi.Output.concat("pulumi-public-subnet-", azs.names[0])},
    )
    public_subnet_b = aws.ec2.Subnet(
        f"{stage}-publicSubnetB-{project_name}",
        vpc_id=vpc.id,
        cidr_block="10.0.2.0/24",
        availability_zone=azs.names[1],
        map_public_ip_on_launch=True,
        tags={"Name": pulumi.Output.concat("pulumi-public-subnet-", azs.names[1])},
    )
    aws.ec2.RouteTableAssociation(f"{stage}-rtaA-{project_name}",
        subnet_id=public_subnet_a.id, route_table_id=public_rt.id)
    aws.ec2.RouteTableAssociation(f"{stage}-rtaB-{project_name}",
        subnet_id=public_subnet_b.id, route_table_id=public_rt.id)

    # Private subnets (A/B) — NO public IPs
    private_subnet_a = aws.ec2.Subnet(
        f"{stage}-privateSubnetA-{project_name}",
        vpc_id=vpc.id,
        cidr_block="10.0.101.0/24",
        availability_zone=azs.names[0],
        map_public_ip_on_launch=False,
        tags={"Name": pulumi.Output.concat("pulumi-private-subnet-", azs.names[0])},
    )
    private_subnet_b = aws.ec2.Subnet(
        f"{stage}-privateSubnetB-{project_name}",
        vpc_id=vpc.id,
        cidr_block="10.0.102.0/24",
        availability_zone=azs.names[1],
        map_public_ip_on_launch=False,
        tags={"Name": pulumi.Output.concat("pulumi-private-subnet-", azs.names[1])},
    )

    # ONE NAT Gateway in publicSubnetA
    nat_eip = aws.ec2.Eip(f"{stage}-nat-eip-{project_name}", domain="vpc")
    nat_gw = aws.ec2.NatGateway(
        f"{stage}-natgw-{project_name}",
        subnet_id=public_subnet_a.id,
        allocation_id=nat_eip.id,
        tags={"Name": f"{stage}-natgw-{project_name}"},
    )

    # Private route tables → NAT (both AZs point to the single NAT)
    private_rt_a = aws.ec2.RouteTable(f"{stage}-privateRT-A-{project_name}", vpc_id=vpc.id)
    aws.ec2.Route(f"{stage}-privateRoute-A-{project_name}",
        route_table_id=private_rt_a.id, destination_cidr_block="0.0.0.0/0",
        nat_gateway_id=nat_gw.id)
    aws.ec2.RouteTableAssociation(f"{stage}-privateRTA-A-{project_name}",
        subnet_id=private_subnet_a.id, route_table_id=private_rt_a.id)

    private_rt_b = aws.ec2.RouteTable(f"{stage}-privateRT-B-{project_name}", vpc_id=vpc.id)
    aws.ec2.Route(f"{stage}-privateRoute-B-{project_name}",
        route_table_id=private_rt_b.id, destination_cidr_block="0.0.0.0/0",
        nat_gateway_id=nat_gw.id)
    aws.ec2.RouteTableAssociation(f"{stage}-privateRTA-B-{project_name}",
        subnet_id=private_subnet_b.id, route_table_id=private_rt_b.id)

    return [
        vpc,
        [public_subnet_a, public_subnet_b],
        [private_subnet_a, private_subnet_b],
    ]


def alb_alias_record(stage: str, project_name, alb: aws.lb.LoadBalancer):

    hosted_zone = aws.route53.get_zone(name=DOMAIN_NAME)

    root_alias = aws.route53.Record(
        f"{stage}-rootAlias-{project_name}",
        zone_id = hosted_zone.zone_id,
        name    = DOMAIN_NAME,        # "" also works for apex
        type    = "A",
        aliases = [aws.route53.RecordAliasArgs(
            name    = alb.dns_name,   # dualstack.<lb-id>.<region>.elb.amazonaws.com
            zone_id = alb.zone_id,    # Pulumi gives you the canonical zone ID
            evaluate_target_health = False,
        )],
    )

    # Optional IPv6
    root_alias_aaaa = aws.route53.Record(
        f"{stage}-rootAliasAAAA-{project_name}",
        zone_id = hosted_zone.zone_id,
        name    = DOMAIN_NAME,
        type    = "AAAA",
        aliases = [aws.route53.RecordAliasArgs(
            name    = alb.dns_name,
            zone_id = alb.zone_id,
            evaluate_target_health = False,
        )],
    )

    return root_alias, root_alias_aaaa


def cdn_alias_record(stage: str, project_name, cdn: aws.cloudfront.Distribution) -> aws.route53.Record:

    hosted_zone = aws.route53.get_zone(name=DOMAIN_NAME)

    record = aws.route53.Record(
        f"{stage}-cdnAliasRecord-{project_name}",
        zone_id=hosted_zone.zone_id,
        name = "static." + DOMAIN_NAME,
        type="A",
        aliases=[aws.route53.RecordAliasArgs(
            name=cdn.domain_name,
            zone_id="Z2FDTNDATAQYW2",
            evaluate_target_health=False,
        )]
    )
    return record


def cdn_certificate(stage: str, project_name: str):
    """us-east-1 cert for CloudFront static sub-domain."""
    us_east_1 = aws.Provider(
        f"{stage}-us-east-1",
        region="us-east-1",
    )

    cert = aws.acm.Certificate(
        f"{stage}-cf-cert-{project_name}".replace("_", "-"),
        domain_name=f"static.{DOMAIN_NAME}",
        validation_method="DNS",
        opts=pulumi.ResourceOptions(provider=us_east_1),
    )

    zone = aws.route53.get_zone(name=DOMAIN_NAME)

    val = aws.route53.Record(
        f"{stage}-cf-cert-val-{project_name}".replace("_", "-"),
        zone_id=zone.zone_id,
        name=cert.domain_validation_options[0].resource_record_name,
        type=cert.domain_validation_options[0].resource_record_type,
        records=[cert.domain_validation_options[0].resource_record_value],
        ttl=60,
        allow_overwrite=True,
    )

    cert_validation = aws.acm.CertificateValidation(
        f"{stage}-cf-cert-validation-{project_name}".replace("_", "-"),
        certificate_arn=cert.arn,
        validation_record_fqdns=[val.fqdn],
        opts=pulumi.ResourceOptions(provider=us_east_1),
    )

    return cert_validation.certificate_arn


def alb(stage: str, project_name: str, subnet_ids: pulumi.Input[list[str]]):
    first_subnet = aws.ec2.get_subnet_output(id=subnet_ids[0])

    alb_sg = aws.ec2.SecurityGroup(
        f"{stage}-alb-sg-{project_name}",
        vpc_id=first_subnet.vpc_id,
        description="ALB SG: allow 80/443",  # ascii dash
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(protocol="tcp", from_port=80,  to_port=80,  cidr_blocks=["0.0.0.0/0"]),
            aws.ec2.SecurityGroupIngressArgs(protocol="tcp", from_port=443, to_port=443, cidr_blocks=["0.0.0.0/0"]),
        ],
        egress=[aws.ec2.SecurityGroupEgressArgs(protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"])],
    )

    lb = aws.lb.LoadBalancer(
        f"{stage}-alb-{project_name}".replace("_", ""),
        internal=False,
        load_balancer_type="application",
        security_groups=[alb_sg.id],
        subnets=subnet_ids,
    )

    tg = aws.lb.TargetGroup(
        f"{stage}-tg-{project_name}".replace("_", "-"),
        port=8000,
        protocol="HTTP",
        target_type="ip",
        vpc_id=first_subnet.vpc_id,
        health_check=aws.lb.TargetGroupHealthCheckArgs(
            path="/health", matcher="204", interval=30, timeout=5,
            healthy_threshold=2, unhealthy_threshold=2,
        ),
    )

    # Regional ACM cert for apex (same region as ALB)
    zone = aws.route53.get_zone(name=DOMAIN_NAME)
    alb_cert = aws.acm.Certificate(
        f"{stage}-alb-cert-{project_name}",
        domain_name=DOMAIN_NAME,
        validation_method="DNS",
    )

    alb_val = aws.route53.Record(
        f"{stage}-alb-cert-val-{project_name}",
        zone_id=zone.zone_id,
        name=alb_cert.domain_validation_options[0].resource_record_name,
        type=alb_cert.domain_validation_options[0].resource_record_type,
        records=[alb_cert.domain_validation_options[0].resource_record_value],
        ttl=60,
    )

    alb_cert_validation = aws.acm.CertificateValidation(
        f"{stage}-alb-cert-validation-{project_name}",
        certificate_arn=alb_cert.arn,
        validation_record_fqdns=[alb_val.fqdn],
    )

    # HTTPS listener (port 443)
    listener = aws.lb.Listener(
        f"{stage}-https-listener-{project_name}",
        load_balancer_arn=lb.arn,
        port=443,
        protocol="HTTPS",
        ssl_policy="ELBSecurityPolicy-TLS13-1-2-2021-06",
        certificate_arn=alb_cert.arn,
        default_actions=[aws.lb.ListenerDefaultActionArgs(type="forward", target_group_arn=tg.arn)],
        opts=pulumi.ResourceOptions(depends_on=[alb_cert_validation]),
    )

    # HTTP -> HTTPS redirect
    aws.lb.Listener(
        f"{stage}-http-redirect-{project_name}",
        load_balancer_arn=lb.arn,
        port=80,
        protocol="HTTP",
        default_actions=[aws.lb.ListenerDefaultActionArgs(
            type="redirect",
            redirect=aws.lb.ListenerDefaultActionRedirectArgs(protocol="HTTPS", port="443", status_code="HTTP_301"),
        )],
    )

    pulumi.export(f"{stage}_alb_dns", lb.dns_name)
    return lb, tg, listener, alb_sg


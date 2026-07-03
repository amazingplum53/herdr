"""An AWS Python Pulumi program"""

import pulumi
import prod
import dev
import sys
import os

config = pulumi.Config()
stack = pulumi.get_stack()

stack_main = {
    "prod": prod,
    "dev": dev,
}.get(stack)

from utils.variables import load_variables

load_variables(stack, container_name = "dev")

if stack_main is None:
    raise ValueError(f"Unsupported stack: {stack}")

stack_main.deploy(stack, os.environ['PROJECT_NAME'])

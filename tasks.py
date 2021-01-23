from invoke import task, Collection
import boto3
import os
from pathlib import Path
import hashlib
import re

BASE_PATH = str(Path(__file__).parent.absolute())
VARIABLES_PATH = "../variables.tfvars"

def _compose_path(path: str) -> str:
    return str(Path(BASE_PATH, path).absolute())

PROJECT_PATHS = {
    "app": _compose_path("infrastructure/app"),
    "bootstrap": _compose_path("infrastructure/bootstrap")
}

#####################
# Cloud invocations #
#####################

@task(name="plan")
def cloud_plan(ctx, project):
    with ctx.cd(PROJECT_PATHS[project]):
        ctx.run(f"terraform plan --var-file {VARIABLES_PATH}")

@task(name="apply")
def cloud_apply(ctx, project):
    with ctx.cd(PROJECT_PATHS[project]):
        ctx.run("terraform taint --allow-missing aws_lambda_function.apgnd_lambda_func")
        ctx.run("terraform taint --allow-missing aws_lambda_permission.apigw")
        ctx.run(f"terraform apply --var-file {VARIABLES_PATH}")

@task(name="destroy")
def cloud_destroy(ctx, project):
    with ctx.cd(PROJECT_PATHS[project]):
        ctx.run(f"terraform destroy --var-file {VARIABLES_PATH}")

@task(name="pack")
def cloud_pack(ctx):
    with ctx.cd(BASE_PATH):
        ctx.run("pip install -r requirements.txt --target package/")
        ctx.run("zip -r lambda_function.zip src/*")

    with ctx.cd(_compose_path("package")):
        ctx.run("zip -r ../lambda_function.zip ./")
    
@task(name="push")
def cloud_push(ctx, archive):
    artifacts_bucket = None

    with ctx.cd(_compose_path(PROJECT_PATHS['bootstrap'])):
        out = ctx.run("terraform output", hide="out").stdout
        artifacts_bucket_match = re.match("artifacts_bucket_name = (?P<bucket_name>[0-9a-zA-Z\-]+)\n", out)
        artifacts_bucket = artifacts_bucket_match.group('bucket_name')

    with ctx.cd(BASE_PATH):
        ctx.run(
            f"aws s3 cp {archive} s3://{artifacts_bucket}", hide="out"
        )

    print(f"Uploaded {archive} to s3 ({artifacts_bucket})!")

#####################
# Local invocations #
#####################


@task(name="start")
def local_start(ctx):
    ctx.run("docker-compose up -d --build")


@task(name="stop")
def local_stop(ctx):
    ctx.run("docker-compose down")


@task(
    name="invoke",
    help={
        "function_name": "Name of the Lambda to invoke locally (as defined in the Cloudformation template)",
        "payload": "JSON payload to include in the trigger event",
    },
)
def local_invoke(ctx, function_name, payload):
    ctx.run(
        f"aws lambda invoke --endpoint http://localhost:9001 --no-sign-request --function-name {function_name} --log-type Tail --payload {payload} {function_name}_out.json"
    )

#####################
# Other invocations #
####################

@task(name="lock")
def lock_requirements(ctx):
    with ctx.cd(BASE_PATH):
        ctx.run("python -m piptools compile requirements.in", hide="both")
        ctx.run("python -m piptools compile requirements_dev.in --output-file requirements_dev.txt", hide="both")

@task(name="update")
def update_requirements(ctx, env, package):
    deps = None

    if env == "prod":
        deps = "requirements.in"
    elif env == "dev":
        deps = "requirements_dev.in"
    else:
        raise ValueError("Invalid env")

    with ctx.cd(BASE_PATH):
        ctx.run(f"python -m piptools compile {deps} --upgrade-package {package}")

@task(name="lint")
def lint(ctx, fix=False):
    with ctx.cd(BASE_PATH):
        ctx.run("black **/*.py" + (" --check" if not fix else ""))

@task(name="test")
def test(ctx):
    with ctx.cd(BASE_PATH):
        ctx.run("pytest --cov=src")

ns = Collection()

local = Collection("local")
local.add_task(local_start)
local.add_task(local_stop)
local.add_task(local_invoke)

cloud = Collection("cloud")
cloud.add_task(cloud_plan)
cloud.add_task(cloud_apply)
cloud.add_task(cloud_destroy)
cloud.add_task(cloud_pack)
cloud.add_task(cloud_push)

project = Collection("requirements")
project.add_task(lock_requirements)
project.add_task(update_requirements)

ns.add_collection(local)
ns.add_collection(cloud)
ns.add_collection(project)

ns.add_task(lint)
ns.add_task(test)

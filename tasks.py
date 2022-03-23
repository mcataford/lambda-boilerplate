from invoke import task, Collection
import boto3
import os
from pathlib import Path
import hashlib
import re
from typing import List, Dict

BASE_PATH = str(Path(__file__).parent.absolute())
VARIABLES_PATH = "../variables.tfvars"

HELP_SEGMENTS = {
    "project": "Project name, either app or bootstrap",
    "archive": "Archive file",
    "function_name": "Name of the Lambda to invoke locally (as defined in the Cloudformation template)",
    "payload": "JSON payload to include in the trigger event",
    "fix": "Whether to fix errors",
    "env": "Environment (dev or prod)",
    "package": "Target package (incl. range)",
}


def _compose_path(path: str) -> str:
    return str(Path(BASE_PATH, path).absolute())


def _build_help_dict(segments: List[str]) -> Dict[str, str]:
    return {segment: HELP_SEGMENTS[segment] for segment in segments}


PROJECT_PATHS = {
    "app": _compose_path("infrastructure/app"),
    "bootstrap": _compose_path("infrastructure/bootstrap"),
}

#####################
# Cloud invocations #
#####################


@task(name="plan", help=_build_help_dict(["project"]))
def cloud_plan(ctx, project):
    """
    Builds the Terraform plan for the given project.
    """
    with ctx.cd(PROJECT_PATHS[project]):
        ctx.run(f"terraform plan --var-file {VARIABLES_PATH}")


@task(name="apply", help=_build_help_dict(["project"]))
def cloud_apply(ctx, project):
    """
    Applies infrastructure changes to the given project.
    """
    with ctx.cd(PROJECT_PATHS[project]):
        ctx.run("terraform taint --allow-missing aws_lambda_function.apgnd_lambda_func")
        ctx.run("terraform taint --allow-missing aws_lambda_permission.apigw")
        ctx.run(f"terraform apply --var-file {VARIABLES_PATH}")


@task(name="destroy", help=_build_help_dict(["project"]))
def cloud_destroy(ctx, project):
    """
    Destroys resources associated with the given project.
    """
    with ctx.cd(PROJECT_PATHS[project]):
        ctx.run(f"terraform destroy --var-file {VARIABLES_PATH}")


@task(name="pack")
def cloud_pack(ctx):
    """
    Prepares and packages the source code for lambdas.
    """
    with ctx.cd(BASE_PATH):
        ctx.run("pip install -r requirements.txt --target package/")
        ctx.run("zip -r lambda_function.zip src/*")

    with ctx.cd(_compose_path("package")):
        ctx.run("zip -r ../lambda_function.zip ./")


@task(name="push", help=_build_help_dict(["archive"]))
def cloud_push(ctx, archive):
    """
    Pushes the given archive to S3.
    """
    artifacts_bucket = None

    with ctx.cd(_compose_path(PROJECT_PATHS["bootstrap"])):
        out = ctx.run("terraform output", hide="out").stdout
        artifacts_bucket_match = re.match(
            "artifacts_bucket_name = (?P<bucket_name>[0-9a-zA-Z\-]+)\n", out
        )
        artifacts_bucket = artifacts_bucket_match.group("bucket_name")

    with ctx.cd(BASE_PATH):
        ctx.run(f"aws s3 cp {archive} s3://{artifacts_bucket}", hide="out")

    print(f"Uploaded {archive} to s3 ({artifacts_bucket})!")


#####################
# Local invocations #
#####################


@task(name="start")
def local_start(ctx):
    """
    Starts your stack locally.
    """
    ctx.run("docker-compose up -d --build")


@task(name="stop")
def local_stop(ctx):
    """
    Stops your local stack.
    """
    ctx.run("docker-compose down")


@task(
    name="invoke",
    help=_build_help_dict(["function_name", "payload"]),
)
def local_invoke(ctx, function_name, payload):
    """
    Triggers the local lambda with the given payload
    """
    ctx.run(
        f"aws lambda invoke --endpoint http://localhost:9001 --no-sign-request --function-name {function_name} --log-type Tail --payload {payload} {function_name}_out.json"
    )


#####################
# Other invocations #
####################

@task(name="lint", help=_build_help_dict(["fix"]))
def lint(ctx, fix=False):
    """
    Lints
    """
    with ctx.cd(BASE_PATH):
        ctx.run("black *.py **/*.py" + (" --check" if not fix else ""))


@task(name="test")
def test(ctx):
    """
    Runs tests
    """
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

ns.add_collection(local)
ns.add_collection(cloud)

ns.add_task(lint)
ns.add_task(test)

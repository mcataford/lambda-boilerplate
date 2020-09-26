from invoke import task, Collection
import boto3
import os
from pathlib import Path
import hashlib

#####################
# Stack invocations #
#####################


@task(name="teardown-app")
def teardown_app(ctx):
    with ctx.cd("infrastructure"):
        ctx.run("sceptre delete app/app.yaml -y")

@task(name="teardown-bootstrap")
def teardown_bootstrap(ctx):
    with ctx.cd("infrastructure"):
        ctx.run("sceptre delete bootstrap/bootstrap.yaml -y")



@task(name="deploy")
def stack_deploy(ctx):
    path = Path(__file__).parent
    with ctx.cd("infrastructure"):
        ctx.run("sceptre launch bootstrap/bootstrap.yaml -y")

    ctx.run("zip lambda_function.zip src/*")
    with open("lambda_function.zip", "rb") as src:
        srchash = hashlib.md5(src.read()).hexdigest()
        new_archive_name = f"lambda_function_{srchash}.zip"
        ctx.run(f"mv lambda_function.zip {new_archive_name}")

    ctx.run(f"aws s3 cp {new_archive_name} s3://mcat-dev-test-bucket-artifacts-2 && rm {new_archive_name}")

    with ctx.cd("infrastructure"):
        ctx.run(f"sceptre --var source_key={new_archive_name} launch app/app.yaml -y")


#####################
# Local invocations #
#####################


@task(name="start")
def app_start(ctx):
    ctx.run("docker-compose up -d --build")


@task(name="stop")
def app_stop(ctx):
    ctx.run("docker-compose down")


@task(
    name="invoke-function",
    help={
        "function_name": "Name of the Lambda to invoke locally (as defined in the Cloudformation template)",
        "payload": "JSON payload to include in the trigger event",
    },
)
def app_invoke_function(ctx, function_name, payload):
    ctx.run(
        f"aws lambda invoke --endpoint http://localhost:9001 --no-sign-request --function-name {function_name} --log-type Tail --payload {payload} {function_name}_out.json"
    )


ns = Collection()

# Stack invocations manage the Clouformation flows

stack = Collection("stack")
stack.add_task(stack_deploy)
stack.add_task(teardown_app)
stack.add_task(teardown_bootstrap)

# App invocations manage local containers

app = Collection("app")
app.add_task(app_start)
app.add_task(app_stop)
app.add_task(app_invoke_function)

ns.add_collection(stack)
ns.add_collection(app)

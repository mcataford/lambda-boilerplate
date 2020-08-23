from invoke import task, Collection
import os

ARTIFACTS_BUCKET_NAME = os.environ["ARTIFACTS_BUCKET"]
STACK_NAME = os.environ["STACK_NAME"]

###############
# Stack utils #
###############


def _package_source(ctx):
    ctx.run("zip lambda_function.zip src/*")


def _create_artifacts_bucket(ctx):
    ctx.run(f"aws s3api create-bucket --acl private --bucket {ARTIFACTS_BUCKET_NAME}")


def _upload_source_to_s3(ctx):
    ctx.run(f"aws s3 cp lambda_function.zip s3://{ARTIFACTS_BUCKET_NAME}")


#####################
# Stack invocations #
#####################


@task(name="deploy")
def stack_deploy(ctx):
    _package_source(ctx)
    _create_artifacts_bucket(ctx)
    _upload_source_to_s3(ctx)
    ctx.run(
        f"aws cloudformation deploy --template-file application.yml --stack-name {STACK_NAME} --parameter-overrides ArtifactsBucketName={ARTIFACTS_BUCKET_NAME} --capabilities CAPABILITY_IAM"
    )


@task(name="update-function")
def stack_update_function(ctx, function_name):
    _package_source(ctx)
    _create_artifacts_bucket(ctx)
    _upload_source_to_s3(ctx)
    ctx.run(
        f"aws lambda update-function-code --function-name {function_name} --s3-bucket {ARTIFACTS_BUCKET_NAME} --s3-key lambda_function.zip"
    )


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
stack.add_task(stack_update_function)

# App invocations manage local containers

app = Collection("app")
app.add_task(app_start)
app.add_task(app_stop)
app.add_task(app_invoke_function)

ns.add_collection(stack)
ns.add_collection(app)

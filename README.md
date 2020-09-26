# lambda-boilerplate
🛠 Skip the boilerplate and start building fun λ things 🛠

![Lambda Boilerplate](https://github.com/mcataford/lambda-boilerplate/workflows/Lambda%20Boilerplate/badge.svg)

## Overview

AWS Lambdas are fun, but often the amount of boilerplate involved in getting a project off the ground hinders the fun. From setting up a local environment to writing out a Cloudformation template, the overhead of Lambda-based greenfield projects can be daunting. No more. Just use this repository as a template or clone it and jump straight into the action! This repository offers a quick template your can use, full with a Docker setup for local development and invocation commands that you can use to package and deploy small Lambdas.

Use this as a foundation and tweak it to your use case!

## Local development

To get started, hit the bootstrap script with `. script/bootstrap`. This will set up a Python 3.8 virtualenv set up with some basic tools that will make your life easier.

The base Lambda handler is at `src/base.py` and all the infrastructure templates and Sceptre configuration are in `infrastructure`.

[Read more about Sceptre](https://sceptre.cloudreach.com/latest/index.html)

[Read more about AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)

### Invocations

This template uses PyInvoke, all commands are of the format `inv <command> <parameters>`.

|Command|Description|
|---|---|
|`app.start`|Start your Lambda in Docker.|
|`app.stop`|Stop and remove the container.|
|`app.invoke-function <function name> <Serialized JSON payload>`|Invokes the given local Lambda by container name|
|`stack.deploy`|Packages your code and deploys the stack|
|`stack.teardown-app`|Tears down the application stack|
|`stack.teardown-bootstrap`|Tears down the bootstrap stack| 

## Deployment

The base setup assumes that your Lambda handler is located in `src.base`. Doing `inv stack.deploy` will zip up your `src` directory, create an S3 bucket for your development artifacts, uploads the source doe archive to S3 and kickstarts the Cloudformation deployment of your stack.

## Contributing

Got suggestions or improvements you'd like to make? Open a PR or [an issue](https://github.com/mcataford/lambda-boilerplate/issues)!

Feature requests should keep in mind that the goal of this boilerplate is to be general enough so that the cost of tailoring it to specific use cases is low.

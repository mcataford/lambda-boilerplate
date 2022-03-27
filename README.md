# lambda-boilerplate
🛠 Skip the boilerplate and start building fun λ things 🛠

![Lambda Boilerplate](https://github.com/mcataford/lambda-boilerplate/workflows/Lambda%20Boilerplate/badge.svg)

## Overview

AWS Lambdas are fun, but often the amount of boilerplate involved in getting a project off the ground hinders the fun. From setting up a local environment to writing out infrastructure templates, the overhead of Lambda-based greenfield projects can be daunting. No more. Just use this repository as a template or clone it and jump straight into the action! This repository offers a quick template your can use, full with a Docker setup for local development and invocation commands that you can use to package and deploy Lambda-based apps.

## Infrastructure configuration

[See documentation](./INFRASTRUCTURE.md)

## Local development

To get started, hit the bootstrap script with `. script/bootstrap`. This will set up a Python 3.8 virtualenv set up with some basic tools that will make your life easier.

The base Lambda handler is at `src/base.py` and all the Terraform configurations are in `infrastructure`.

[Read more about Sceptre](https://sceptre.cloudreach.com/latest/index.html://www.terraform.io/docs/index.html)

[Read more about AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)

### Invocations

This template uses PyInvoke, all commands are of the format `inv <command> <parameters>`.

Use `inv --list` for the full list of commands.

## Deployment

Deployment is in three steps: on first setup, you will need to make sure that your `bootstrap` environment is ready via `inv cloud.apply bootstrap`. Then, you should upload your lambdas' source with `inv cloud.pack` and `inv cloud.push`. Finally, you can deploy your application resources with `inv cloud.deploy app`.

## Contributing

Got suggestions or improvements you'd like to make? Open a PR or [an issue](https://github.com/mcataford/lambda-boilerplate/issues)!

Feature requests should keep in mind that the goal of this boilerplate is to be general enough so that the cost of tailoring it to specific use cases is low.

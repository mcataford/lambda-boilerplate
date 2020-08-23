# lambda-boilerplate
🛠 Skip the boilerplate and start building fun λ things 🛠

## Overview

AWS Lambdas are fun, but often the amount of boilerplate involved in getting a project off the ground hinders the fun. From setting up a local environment to writing out a Cloudformation template, the overhead of Lambda-based greenfield projects can be daunting. No more. Just use this repository as a template or clone it and jump straight into the action! This repository offers a quick template your can use, full with a Docker setup for local development and invocation commands that you can use to package and deploy small Lambdas.

Use this as a foundation and tweak it to your use case!

## Local development

To get started, hit the bootstrap script with `. script/bootstrap`. This will set up a Python 3.8 virtualenv set up with some basic tools that will make your life easier.

### Invocations

This template uses PyInvoke, all commands are of the format `inv <command> <parameters>`.

|Command|Description|
|---|---|
|`app.start`|Starts your Lambda in Docker.|
|`app.stop`|Stop and remove the container.|

## Deployment

The base setup assumes that your Lambda handler is located in `src.base`. Doing `inv stack.deploy` will zip up your `src` directory, create an S3 bucket for your development artifacts, uploads the source doe archive to S3 and kickstarts the Cloudformation deployment of your stack.


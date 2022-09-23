# lambda-boilerplate
🛠 Skip the boilerplate and start building fun λ things 🛠

![Lambda Boilerplate](https://github.com/mcataford/lambda-boilerplate/workflows/Lambda%20Boilerplate/badge.svg)

## Overview

AWS Lambdas are fun, but often the amount of boilerplate involved in getting a project off the ground hinders the fun. From setting up a local environment to writing out infrastructure templates, the overhead of Lambda-based greenfield projects can be daunting. No more. Just use this repository as a template or clone it and jump straight into the action! This repository offers a quick template your can use, full with a Docker setup for local development and invocation commands that you can use to package and deploy Lambda-based apps.

## Local development

The base Lambda handler is at `src/base.py` and all the Terraform configurations are in `infrastructure`.

[Read more about Sceptre](https://sceptre.cloudreach.com/latest/index.html://www.terraform.io/docs/index.html)

[Read more about AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)

### Tooling

All the tooling is implemented using the [One Script to Rule Them
All](https://github.com/github/scripts-to-rule-them-all) paradigm and can be found under `script`.

## Deployment

Deployment is in three steps: on first setup, you will need to make sure that your `bootstrap` environment is ready via `PROJECT=bootstrap . script/apply`. Then, you should prepare your source code package (dependent on the language and framework you're using, you have to supply this bit!) and `ARCHIVE=<path-to-zip> . script/push`. Finally, you can deploy your application resources with `PROJECT=app . script/apply`.

## Contributing

Got suggestions or improvements you'd like to make? Open a PR or [an issue](https://github.com/mcataford/lambda-boilerplate/issues)!

Feature requests should keep in mind that the goal of this boilerplate is to be general enough so that the cost of tailoring it to specific use cases is low.

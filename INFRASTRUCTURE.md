# Infrastructure

## Layout

The infrastructure is split between the `bootstrap` and `app` projects.

The `bootstrap` project sets up an S3 bucket to allow the lambda code to be uploaded and be available for app
deployment.

The `app` project sets up everything else (i.e. lambda function, security groups, API gateways, ...).

## Configuration

Unless you want to change the resources being deployed, you can customize the base infrastructure via the
`infrastructure/common.tfvars` (for anything shared between the `bootstrap` and `app` projects) and
`infrastructure/<project>/variables.tfvars` (for anything specific to one of the projects) files.

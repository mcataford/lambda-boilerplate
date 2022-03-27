VENV=.venv
TERRAFORM=${VENV}/bin/terraform
LAMBDA_PACKAGE=lambda_function.zip

.PHONY: deploy
deploy:
	${TERRAFORM} -chdir=infrastructure/${PROJECT} apply --var-file ./variables.tfvars --var-file ../common.tfvars

.PHONY: plan
plan:
	${TERRAFORM} -chdir=infrastructure/${PROJECT} plan --var-file ./variables.tfvars --var-file ../common.tfvars

.PHONY: destroy
destroy:
	${TERRAFORM} -chdir=infrastructure/${PROJECT} destroy --var-file ./variables.tfvars --var-file ../common.tfvars

.PHONY: prepare
prepare:
	. script/prepare

.PHONY: prepare-and-upload
prepare-and-upload:
	. script/prepare --push

##############################
# Local development recipes. #
##############################

.PHONY: start
start:
	docker-compose up -d --build

.PHONY: stop
stop:
	docker-compose down

.PHONY: invoke
invoke:
	aws lambda invoke --endpoint http://localhost:9001 --no-sign-request --function-name ${FUNCTION_NAME} --log-type Tail --payload ${PAYLOAD} ${FUNCTION_NAME}_out.json

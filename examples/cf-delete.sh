#!/bin/bash -x
. cf-defaults.sh
aws --region "${REGION}" \
	cloudformation delete-stack --stack-name "${STACK_NAME}"

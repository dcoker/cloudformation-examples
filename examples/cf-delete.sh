#!/bin/bash -x
. defaults.sh
aws --region "${REGION}" \
	cloudformation delete-stack --stack-name "${STACK_NAME}"

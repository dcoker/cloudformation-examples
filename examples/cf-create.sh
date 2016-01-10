#!/bin/bash
set -e
. cf-defaults.sh
# Your stack may require you to specify --parameters here. See "aws
# cloudformation create-stack help" for examples. Here's what it might look
# like:
#
#   PARAMETERS=(
#     ParameterKey=NotifyEmail,ParameterValue=\"${NOTIFY_EMAIL_ADDRESS}\",UsePreviousValue=false
#     ParameterKey=HostedZoneId,ParameterValue=XXXXXXXX,UsePreviousValue=false
#   )
#   aws ... --parameters ${PARAMETERS[@]}
aws --region "${REGION}" cloudformation create-stack \
	--stack-name "${STACK_NAME}" \
	--template-body "${TEMPLATE_FILE}" \
	--capabilities CAPABILITY_IAM 
echo __ waiting for stack to finish
sleep "${WAIT_SECONDS}"
while [[ "CREATE_IN_PROGRESS" == "$(aws --region "${REGION}" cloudformation describe-stacks --stack-name "${STACK_NAME}" --query 'Stacks[0].StackStatus' --output text)" ]]; do
	echo __ waiting
	sleep "${WAIT_SECONDS}"
done

aws --region "${REGION}" cloudformation describe-stacks \
	--stack-name "${STACK_NAME}" \
	--query 'Stacks[0].[StackStatus,Outputs]'

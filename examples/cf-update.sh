. defaults.sh
aws --region "${REGION}" cloudformation update-stack \
	--stack-name "${STACK_NAME}" \
	--template-body ${TEMPLATE_FILE} \
	--capabilities CAPABILITY_IAM

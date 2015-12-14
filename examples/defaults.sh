TEMPLATE=${TEMPLATE:-"end-to-end/webserver-with-route53-hostname.json"}
TEMPLATE_FILE=file://./${TEMPLATE}
STACK_NAME=${STACK_NAME:-"${LOGNAME}-$(date +%s)"}
REGION=us-west-2
WAIT_SECONDS=5

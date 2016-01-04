#
# DeleteQueuesCustomResource is a Lambda function intended to be invoked by AWS
# CloudFormation as a custom resource. It deletes SQS queues that might have
# been created during a cluster during its operation.
#
# Queues having names starting with QueueNamePrefix and containing the
# QueueNameSubstring as a substring and with characters trailing after
# QueueNameSubstring will get deleted when the stack is torn down.
#
# See cf-delete-queues-example.json for details.
#
import boto3
import json
import logging
import re
import urllib2
from cfnresponse import send, SUCCESS, FAILED

# Messages sent to logger or stdout or stderr will be logged in CloudWatch Logs
# automatically by the Lambda stack.
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context, sqs_client):
    # We only care when the stack is being deleted.
    if event["RequestType"] != "Delete":
        logger.info("RequestType <> delete")
        return

    # Arbitrary parameters can be passed from the CloudFormation custom
    # resource and they are placed in the ResourceProperties dictionary. You
    # can think of these as function parameters.
    stackName = event["ResourceProperties"]["StackName"]
    queueNamePrefix = event["ResourceProperties"]["QueueNamePrefix"]
    queueNameSubstring = event["ResourceProperties"]["QueueNameSubstring"]
    logger.info("invoked for stackName=%s", stackName)
    logger.info("queue name prefix=%s", queueNamePrefix)
    logger.info("queue url substring=%s", queueNameSubstring)

    queues = sqs_client.list_queues(QueueNamePrefix=queueNamePrefix)
    logger.info("List of queues: %r", queues)
    if not queues.has_key("QueueUrls"):
        logger.info("there are no queues to inspect")
        return
    queue_url_regex = (r"https://.+/" 
        + re.escape(queueNamePrefix) 
        + r".*"
        + re.escape(queueNameSubstring) 
        + r".+$")
    logger.info("Using regex: %r", queue_url_regex)
    for url in queues["QueueUrls"]:
        if not re.match(queue_url_regex, url):
          continue
        logger.info("Deleting: %s", url)
        sqs_client.delete_queue(QueueUrl=url)


def delete_queues_handler(event, context):
    """lambda_handler is the entrypoint of this "function"."""
    logger.info("Request: %s", json.dumps(event))
    # In most other contexts that Lambda is used, the return value is
    # immediately available. However, CloudFormation doesn't use those standard
    # return values, and instead wants the agent to hit a URL to indicate
    # success or failure.  If CloudFormation does not receive an explicit
    # notification, it can only rely on timeouts to detect failure, and that
    # can waste human time.
    #
    # We wrap all the logic in a try/except so that we always try to send
    # CloudFormation a status message.
    try:
        sqs_client = boto3.client('sqs')
        handler(event, context, sqs_client)
        send(event, context, SUCCESS)
    except Exception, e:
        logger.error("Exception: %r", e)
	# There is no point in trying to notify if we for some reason already
	# failed to notify. CloudFormation will eventually time out.
	if not isinstance(e, urllib2.URLError):  
             send(event, context, FAILED)
        raise

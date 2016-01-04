custom-resource-queue-cleanup
=============================

Sometimes your CloudFormation stack will dynamically create resources, but
you'd like to delete those resources when you delete the stack.
CloudFormation's support for Custom Resources and Lambda allows you to use
Lambda to run cleanup operations when a stack is deleted. 

This directory contains an example of how to remove dynamically created SQS
queues.

Demo:

1. Install pip, boto3, and awscli system-wide.
2. Set up virtualenv and build the deployment zip:
  ```
  $ virtualenv venv
  $ . ./venv/bin/activate
  $ pip install -r requirements.txt
  $ ./build.sh
  ```
3. Push the bundled zip to a bucket readable by Lambda (replacing your-bucket-name):
  ```
  $ BUCKET=your-bucket-name ./deploy-s3.sh
  ```
4. Run the example CloudFormation template, create a queue, and observe the results. Be sure to replace your-bucket-name.
  ```
  $ aws cloudformation create-stack \
      --stack-name one-deleter-stack \
      --template-body file://delete-sqs-queues.json \
      --parameters ParameterKey=BucketName,ParameterValue=your-bucket-name \
      --capabilities CAPABILITY_IAM
  ... wait a while until the following command returns Status = CREATE_COMPLETE:
  $ aws cloudformation describe-stacks --stack-name one-deleter-stack
  ... check your CloudWatch Logs dashboard to see the Type=Create call
  $ aws sqs create-queue --queue-name acme_one-deleter-stack
  $ aws sqs list-queues
  $ aws cloudformation delete-stack --stack-name one-deleter-stack 
  ... wait
  $ aws sqs list-queues
  ```

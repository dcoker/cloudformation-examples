# EC2 Roles, Bash, and KMS-encrypted secrets

Use case: you have a secret value (such as a password or API key) and you want
to store it securely and make it usable to a bash script running on an EC2
instance.

Summary of Solution: Create a KMS key. Encrypt the secret under that key. Allow
the role of the machine the ability to decrypt the secret. Update the bash
script to use the awscli to decrypt the secret.

In the examples below:

1. replace XXX with the username of the employee you designate as key adminstrator. This person controls who can use the key and for what purposes and how.
2. replace YYY with the username of the employee you want to be able to encrypt or decrypt.
3. replace PPP with a short label for the customer.
4. replace SSS with your secret
5. if you're not using us-east-1, pass `--region us-west-2` to the awscli.

## Create a KMS Key

You have two options for creating the KMS key. You can use the kms.json
CloudFormation template in this directory, or you can use the AWS Console.

To use the CloudFormation template:

```
aws cloudformation create-stack --stack-name kms-key \
	--template-body file://./kms.json \
	--parameters ParameterKey=AdministratorPrincipal,ParameterValue=user/XXX,UsePreviousValue=false \
		ParameterKey=UserPrincipal,ParameterValue=user/YYY,UsePreviousValue=false \
	--capabilities CAPABILITY_IAM
```

To use the AWS Console:

1. Visit the AWS IAM console
2. Click "encryption keys" in the left
3. Ensure the "Filter" value is set to the region of your choice.
4. Click "Create Key"
5. Enter an alias for the key (such as demonstration-key) and click next.
6. Select the users that you wish to allow to administer this key. This is XXX. Click "next step".
7. Select the users that you wish to be able to use the key. This is YYY. Click "next step".

## Encrypt the Secret

The engineer responsible for the bash script should run:

```
aws kms encrypt --key-id 6d0e2e00-b0ae-4988-b66f-0fa059d928f3 \
	--encryption-context Customer=PPP \
	--plaintext SSS \
        --output text --query CiphertextBlob 
```

Paste the output of that command into your bash script as a bash variable and
commit it to VCS. See below for example.

## Create an IAM Role and Instance Profile for the machine that will consume the secret

Now we grant the role that the instance or person will be using to run this
script the ability to decrypt the encrypted value.

If the instance will already has an Instance Profile and Role specific to the
task at hand, get the ARN of that role. If you need to create that now, do so,
and get the ARN. 

As user XXX or YYY, create a grant for the role, replacing RRR with the full
ARN of the role:

```
aws kms create-grant \
	--key-id 6d0e2e00-b0ae-4988-b66f-0fa059d928f3 \
	--grantee-principal RRR \
	--operations Decrypt \
	--constraints EncryptionContextSubset={Customer=PPP} \
	--name AllowRoleToDecryptPPPGrant  
```

## Decrypt the Secret

Update your bash script to decrypt the value. Example:

```
CIPHERTEXT="CiDQsQVzDzHkGnuQz61niLnOHpNlHTKJD+Y8PpSl4..."
PLAINTEXT=$(aws kms decrypt \
	--ciphertext-blob fileb://<(echo "${CIPHERTEXT}" | base64 -d) \
	--encryption-context Customer=PPP \
	--output text \
	--query Plaintext | base64 -d)
```

You can safely commit CIPHERTEXT to your version control system.

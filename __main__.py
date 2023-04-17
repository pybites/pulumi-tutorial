"""An AWS Python Pulumi program"""

import json

import pulumi
from pulumi_aws import iam, lambda_, s3

# Create an AWS resource (S3 Bucket)
bucket = s3.Bucket('my-bucket-pybites-tutorial-pulumi', 
                   bucket='my-bucket-pybites-tutorial-pulumi')

# Export the name of the bucket
pulumi.export('bucket_name', bucket.id)


# Create an IAM role for the Lambda function
lambda_role = iam.Role("lambda-role",
    name='lambda-role-pybites-tutorial-pulumi',
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com",
            },
        }]
    })
)

# Attach the necessary policy to the IAM role
iam.RolePolicyAttachment("lambdaRolePolicy",
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    role=lambda_role.name
)

# Create a Lambda function
lambda_function = lambda_.Function("lambdaFunction",
    role=lambda_role.arn,
    runtime="python3.9",
    handler="lambda_handler.handler",
    code=pulumi.AssetArchive({
        '.': pulumi.FileArchive('./aws_lambda')
    }),
    timeout=10
)

# Grant the Lambda function read access to the S3 bucket
s3_bucket_policy = s3.BucketPolicy("s3BucketPolicy",
    bucket=bucket.id,
    policy=pulumi.Output.all(bucket_arn=bucket.arn, lambda_function_arn=lambda_function.arn).apply(
        lambda args: json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["s3:GetObject"],
            "Effect": "Allow",
            "Resource": f"{args['bucket_arn']}/*",
            "Principal": {
                "AWS": args['lambda_function_arn'],
            }
        }]
    }))
)

# Create an S3 bucket notification to trigger the Lambda function
s3_bucket_notification = s3.BucketNotification("s3BucketNotification",
    bucket=bucket.id,
    lambda_functions=[{
        "lambda_function_arn": lambda_function.arn,
        "events": ["s3:ObjectCreated:*"]
    }]
)

# Add the necessary permissions for S3 to invoke the Lambda function
lambda_.Permission("lambdaS3ExecutionPermission",
    action="lambda:InvokeFunction",
    function=lambda_function.arn,
    principal="s3.amazonaws.com",
    source_arn=bucket.arn
)


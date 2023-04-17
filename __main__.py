"""An AWS Python Pulumi program"""

import json

import pulumi
from pulumi_aws import iam, lambda_, s3

# Create an AWS resource (S3 Bucket)
bucket = s3.Bucket('my-bucket-pybites-tutorial-pulumi', 
                   bucket='my-bucket-pybites-tutorial-pulumi')

# Export the name of the bucket
pulumi.export('bucket_name', bucket.id)



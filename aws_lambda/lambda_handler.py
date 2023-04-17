import json


def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(f"File uploaded to S3 bucket {bucket}: {key}")

import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

# Put your AWS credentials in a .env file
access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

s3 = boto3.client('s3',region_name='us-west-2')
bucket_name='custom-labels-console-us-west-2-9d34a728b0'
File_key='path/to/image.jpg'
client = boto3.client(
    service_name="rekognition",
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name="us-west-2",
)
filesofphotosS3input=s3.list_objects_v2(Bucket=bucket_name)
if 'Contents' in filesofphotosS3input:
    for obj in filesofphotosS3input['Contents']:
        print(f"File: {obj['Key']}")
else:
    print("No files found in the bucket.")



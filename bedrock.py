import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

vehicle_types = [
    'vehicle', 'car', 'truck', 'suv', 'van', 'bus', 
    'motorcycle', 'taxi', 'ambulance', 'firetruck', 'police car'
]

vehicle_bounding_boxes=[]

# Put your AWS credentials in a .env file
access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

s3 = boto3.client('s3',region_name='us-west-2')
bucket_name='custom-labels-console-us-west-2-9d34a728b0'
File_key='path/to/image.jpg'
rekognition = boto3.client(
    service_name="rekognition",
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name="us-west-2",
)

response = s3.list_objects_v2(Bucket=bucket_name)
image_files = [item['Key'] for item in response.get('Contents', []) if item['Key'].lower().endswith(('png', 'jpg', 'jpeg'))]
# Analyze each image in the S3 bucket
for image_file in image_files:
    print(f"Analyzing {image_file}...")
    
    # Call Rekognition to detect labels
    response = rekognition.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': image_file
            }
        },
        MaxLabels=20,  # Adjust based on your needs
        MinConfidence=40  # Confidence threshold
    )
    print(response)
    quit
    # Print analysis results
    print(f"Results for {image_file}:")
    car_count=0
    for label in response['Labels']:
        print(f"- {label['Name']}: {label['Confidence']:.2f}%")
        if label['Name'].lower() in vehicle_types:
            car_count+=len(label.get('Instances',[]))
        if label['Name'] == 'Traffic Jam':
            for instance in label['Instances']:
                vehicle_bounding_boxes.append(instance['BoundingBox'])
    print(car_count)
    car_count=0

for box in vehicle_bounding_boxes:
    print(f"Bounding Box: {box}")
        
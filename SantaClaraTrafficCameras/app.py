import time
import json
import requests
from datetime import datetime
from flask import Flask, jsonify, render_template, Response
from threading import Thread
import base64
import boto3
import os

app = Flask(__name__)

image_data = None
camera="GAOldGlory"
counter = 0

rekognition = boto3.client('rekognition', region_name='us-west-2')
s3 = boto3.client(
    's3',
    aws_access_key_id='',
    aws_secret_access_key='',
    region_name='us-west-2'
)
bucket_name = 'custom-labels-console-us-west-2-9d34a728b0'
response = s3.list_objects_v2(Bucket=bucket_name)


def get_image(counter):
    image_id = f"{counter:03}"
    url = f"http://trafficcam.santaclaraca.gov/Feeds/{camera}/snap_{image_id}_c1.jpg"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to download image {image_id}")
        return None
    
    image_bytes = response.content
    return image_bytes

def export_json():
    global counter
    image_bytes = image_data
    if None:
        return None

    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    return {
        "camera": camera,
        "event": {
            "counter": counter,
            "url": f"http://trafficcam.santaclaraca.gov/Feeds/{camera}/snap_{counter:03}_c1.jpg",
            "event_timestamp": datetime.utcnow().isoformat(),
            "image_binary": image_base64
        }
    }


def fetch_image():
    global image_data,counter
    counter = 0
    
    while True:
        event_data = get_image(counter)
        
        if event_data:
            image_data = event_data
            time.sleep(0.5)  
        counter = (counter+1)%256

@app.route('/traffic-image-json', methods=['GET'])
def get_traffic_image_json():
    if image_data:
        return jsonify(export_json(image_data))
    else:
        return jsonify({"error": "Image not available"}), 404

@app.route('/traffic-image-raw', methods=['GET'])
def get_traffic_image_raw():
    if image_data:
        return Response(image_data, content_type='image/jpeg')
    else:
        return jsonify({"error": "Image not available"}), 404

@app.route('/traffic-image-rekog', methods=['GET'])
def do_rekog():
    if image_data:
        # Define S3 object key
        s3_key = f"images/snap_{counter:03}.jpg"

        # Upload the image to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=image_data,
            ContentType='image/jpeg'
        )
        # Call Rekognition to detect labels on the image
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': s3_key
                }
            },
            MaxLabels=10,  # Adjust based on your needs
            MinConfidence=40,  # Confidence threshold
            Features=["GENERAL_LABELS"], 
            Settings={
                'GeneralLabels': {
                    'LabelInclusionFilters': [
                        'Car', "Headlight","Light"
                    ]  
                }
            }
        )
        labels = []
        car_count=0
        light_count = 0
        headlight_count = 0
        for label in response['Labels']:
            if label['Name']== 'Car':
                car_count=len(label.get('Instances',[]))
            labels.append(f"- {label['Name']}: {label['Confidence']:.2f}%")
        print("\n".join(labels))

        image_base64 = base64.b64encode(image_data).decode('utf-8')

        return render_template(
            'rekog_result.html', 
            image_data=image_base64,
            result_json={
                "message": "Rekognition results", 
                "labels": labels, 
                "car_count": car_count,
            }
        )
    else:
        return jsonify({"error": "Image not available"}), 404


def start_background_task():
    thread = Thread(target=fetch_image)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    start_background_task()
    app.run(debug=True, host="0.0.0.0", port=3000)


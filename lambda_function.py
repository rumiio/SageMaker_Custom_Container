import os
import boto3
import json

# grab environment variables
ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
runtime= boto3.client('runtime.sagemaker')
s3 = boto3.resource('s3')

def lambda_handler(event, context):
    
    BUCKET_NAME = 'your-bucket-name' 
    OBJECT_KEY = 'SageMaker_Custom_Container/data/glass_bottle.jpg' #plastic_bottle.jpg' #paper.jpg' 
    file_name = '/tmp/glass_bottle.jpg'
    s3.Bucket(BUCKET_NAME).download_file(OBJECT_KEY, file_name)
    
    payload = ''

    with open(file_name, 'rb') as f:
        payload = f.read()
        payload = bytearray(payload)
    
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                       ContentType='application/x-image',
                                       Body=payload)

    result = json.loads(response['Body'].read().decode())
    print(result)
    pred = result['predictions']['class']
    
    return pred 
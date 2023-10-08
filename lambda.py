import json
import boto3
import base64
import lambda1
import zipfile
import os
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    print(key)
    bucket = event['s3_bucket']
    uri = "/".join([bucket, key])
    print(uri)
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    lambda1.download_data(uri)
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }



def download_data(s3_input_uri):
    s3 = boto3.client('s3')
    input_bucket = s3_input_uri.split('/')[0]
    input_object = '/'.join(s3_input_uri.split('/')[1:])
    file_name = '/tmp/image.png'
    s3.download_file(input_bucket, input_object, file_name)




# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2023-10-08-20-50-22-010'
session= boto3.Session()
runtime = boto3.Session().client('sagemaker-runtime')

def lambda_handler2(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']['image_data'])
    
    response = runtime.invoke_endpoint(EndpointName = ENDPOINT, ContentType = 'image/png',Body = image)
    
    predictions = json.loads(response['Body'].read().decode())

    # Instantiate a Predictor
    #predictor = sagemaker.predictor.Predictor(endpoint_name=ENDPOINT,sagemaker_session=sagemaker.Session())

    # For this model the IdentitySerializer needs to be "image/png"
    #predictor.serializer = IdentitySerializer("image/png")
    
    # Make a prediction:
    #inferences = predictor.predict(image)
    
    # We return the data back to the Step Function    
    event['inferences'] = predictions
    return { 'statusCode': 200, 'body': event }





THRESHOLD = .8

def lambda_handler3(event, context):
    # Grab the inferences from the event
    inferences = event['body']['inferences']
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(inferences)>THRESHOLD## TODO: fill in
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error


    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }

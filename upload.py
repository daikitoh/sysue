import boto3
from datetime import datetime
from fastapi import UploadFile, File
from dotenv import load_dotenv
import os
import json
import base64
import cgi
import io
import uuid

s3 = boto3.resource('s3')
REGION_NAME = 'us-east-1'
BUCKET_NAME = 'sysue-bucket'
DIR = 'images'

def upload_file(file: UploadFile = File(...)):

    load_dotenv()

    REGION_NAME = os.environ.get('AWS_REGION')

    BUCKET_NAME = os.environ.get('BUCKET')

    DIR = 'images'
    
    bucket = s3.Bucket(BUCKET_NAME)
    
    key = datetime.now().strftime('%Y%m%d%H%M%S') + str(uuid.uuid4())[:20] + '.' + file.filename.split('.')[-1]
    print("key: %s" % key)
    bucket.put_object(Body=file.file, Key=DIR+'/'+key)

    # response = s3.put_object(
    #     Body = file.file,
    #     Bucket = bucket,
    #     Key = f"{dir}/{key}"
    # )
        
    file_url = 'https://%s.s3-website-%s.amazonaws.com/%s' % (BUCKET_NAME, REGION_NAME, DIR+'/'+key)
    
    return {
        'statusCode': 200,
        # 'headers': {
        #     "Access-Control-Allow-Origin": "*",
        #     "Access-Control-Allow-Methods": "POST,GET,PUT,DELETE",
        #     "Access-Control-Allow-Headers": "Content-Type"
        # },
        'body': json.dumps(file_url)
    }




def lambda_handler(event, context):
    print(event)
    body = base64.b64decode(event['body'])
    fp = io.BytesIO(body)
    print(body)
    print(fp)
    
    environ = {'REQUEST_METHOD': 'POST'}
    headers = {
        'content-type': event['headers']['content-type'],
        'content-length': len(body)
    }


import boto3
from datetime import datetime
from fastapi import UploadFile, File
from dotenv import load_dotenv
import os

def upload_file(file: UploadFile = File(...), title: str = ""):

    load_dotenv()

    region_name = os.environ.get('AWS_REGION')

    bucket = os.environ.get('BUCKET')

    dir = 'images'

    file.filename.split('.')[-1]

    key = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + str(title.encode('utf-8')) + extension

    s3 = boto3.client('s3', region_name = region_name)
    
    response = s3.put_object(
        Body = file.file,
        Bucket = bucket,
        Key = f"{dir}/{key}"
    )
    # Body=json.dumps(json_data).encode()

    file_url = 'https://%s.s3-website-%s.amazonaws.com/%s' % (bucket, region_name, dir+'/'+key)

    response = {
        'file_url': file_url
    }

    return response
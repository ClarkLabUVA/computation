import os
import sys
import requests
from minio import Minio
from minio.error import ResponseError

MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')
OUTPUT = os.environ.get('OUTPUT')
ORS_URL = os.environ.get("ORS_URL","http://mds.ors/")

minioClient = Minio(MINIO_URL,
                  access_key=MINIO_ACCESS_KEY,
                  secret_key=MINIO_SECRET,
                  secure=False)

bucket = OUTPUT.split('/')[0]
rest = '/'.join(OUTPUT.split('/')[1:])

def upload(file,name):
    with open(file, 'rb') as file_data:
        file_stat = os.stat(file)
        minioClient.put_object(bucket, rest + '/' + name,
                               file_data, file_stat.st_size)

path = '/output'
for root, dirs, files in os.walk(path):
    for name in files:
        file_loc = root + '/' + name
        upload(file_loc,name)

import os
import sys
import requests
from minio import Minio
from minio.error import ResponseError

MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')

ORS_URL = os.environ.get("ORS_URL","http://mds.ors/")

minioClient = Minio(MINIO_URL,
                  access_key=MINIO_ACCESS_KEY,
                  secret_key=MINIO_SECRET,
                  secure=False)

def get_distribution(id):
    """Validates that given identifier exists in Mongo.
        Returns location in minio. """
    if isinstance(id,list):
        locations = []
        names = []
        for i in id:
            location, name = get_distribution(i)
            locations.append(location)
            names.append(name)
        return locations, names
    r = requests.get(ORS_URL + id)
    if r.status_code != 200:
        return False, "Identifier Doesn't Exist."
    try:
        data_dict = r.json()
        data_url = data_dict['distribution'][0]['contentUrl']
        file_location = '/'.join(data_url.split('/')[1:])
        name = data_dict['name']
    except:
        return False, "Distribution not found. Or distribution formatting different than expected."
    return file_location, name

def download_all(locations,names):
    for i in range(len(locations)):
        bucket = locations[i].split('/')[0]
        rest = "/".join(locations[i].split('/')[1:])
        data = minioClient.get_object(bucket, rest)
        with open('/script/' + rest.split('/')[-1], 'wb') as file_data:
            for d in data.stream(32*1024):
                file_data.write(d)

data_ids = os.environ.get("SCRIPT")
data_ids = data_ids.replace('[','').replace(']','').split(',')
locations, names = get_distribution(data_ids)
download_all(locations,names)

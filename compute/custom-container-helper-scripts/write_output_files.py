import os
import sys
import requests
from minio.error import ResponseError
import json
ORS_URL = os.environ.get("ORS_URL","http://mds.ors/")
JOBID = os.environ.get("JOBID","testestest")



def mint_and_upload(file_loc,name,comp_id):

    meta = {
        'name':name,
        "eg:generatedBy":{'@id':comp_id},
        "folder":JOBID
    }

    id = transfer(meta,file_loc)

    return id

def transfer(metadata,location):
    files = {
        'files':open(location,'rb'),
        'metadata':json.dumps(metadata),
    }
    url = 'http://transfer-service/data/'
    r = requests.post(url,files=files)
    data_id = r.json()['Minted Identifiers'][0]
    return data_id



def update_job_id(job_id,output_ids):
    '''
    Updates Job Identifier to show completion or
    failure of job
    '''

    meta = {
        'eg:supports':output_ids
    }
    r = requests.put(ORS_URL + job_id,data = json.dumps(meta))
    return

data_ids = os.environ.get("DATA").split(',')
script_id = os.environ.get("SCRIPT")


path = '/outputs'
supported_ids = []
for root, dirs, files in os.walk(path):
    for name in files:
        file_loc = root + '/' + name
        minted = mint_and_upload(file_loc,name,'ark:99999/' + JOBID)
        supported_ids.append(minted)
update_job_id('ark:99999/' + JOBID,supported_ids)

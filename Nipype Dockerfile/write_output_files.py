import os
import sys
import requests
from minio.error import ResponseError
import json
ORS_URL = os.environ.get("ORS_URL","http://mds.ors/")
JOBID = os.environ.get("JOBID","testestest")
TRANSFER_URL = os.environ.get("ORS_URL","http://transfer/")
EVI_PREFIX = 'evi:'


def mint_and_upload(file_loc,name,comp_id):

    meta = {
        'name':name,
        EVI_PREFIX + "generatedBy":{'@id':comp_id},
        "folder":JOBID
    }

    id = transfer(meta,file_loc)

    return id

def transfer(metadata,location):
    files = {
        'files':open(location,'rb'),
        'metadata':json.dumps(metadata),
    }
    url = TRANSFER_URL + 'data/'
    r = requests.post(url,files=files)
    data_id = r.json()['Minted Identifiers'][0]
    return data_id



def update_job_id(job_id,output_ids,id_dict):
    '''
    Updates Job Identifier to show completion or
    failure of job
    '''

    meta = {
        'fileIDJson':id_dict,
        EVI_PREFIX + 'supports':output_ids
    }
    r = requests.put(ORS_URL + job_id,data = json.dumps(meta))
    return

data_ids = os.environ.get("DATA").split(',')
script_id = os.environ.get("SCRIPT")

with open('/meta/inputs.json') as json_file:
    already_minted = json.load(json_file)

supported_ids = []
path = '/outputs'
for root, dirs, files in os.walk(path):
    for name in files:
        file_loc = root + '/' + name
        if file_loc in already_minted.keys():
            supported_ids.append(already_minted[file_loc])
            continue
        else:
            minted = mint_and_upload(file_loc,name,'ark:99999/' + JOBID)
            already_minted[file_loc] = minted
            supported_ids.append(minted)
with open('/meta/inputs.json', 'w') as outfile:
    json.dump(already_minted, outfile)
id_dict = mint_and_upload('/meta/inputs.json',"Job outputs for " + str('ark:99999/' + JOBID),'ark:99999/' + JOBID)
id_dict = mint_and_upload('/meta/output_ids.json',"Nipype outputs for " + str('ark:99999/' + JOBID),'ark:99999/' + JOBID)
update_job_id('ark:99999/' + JOBID,supported_ids,id_dict)

#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import os
import sys
import requests
from minio.error import ResponseError
import json
ORS_URL = os.environ.get("ORS_URL","http://mds.ors/")
JOBID = os.environ.get("JOBID","testestest")
TRANSFER_URL = os.environ.get("TRANSFER_URL","http://transfer/")
NS = os.environ.get("NAMESPACE","99999")
EVI_PREFIX = 'evi:'
TOKEN =  os.environ.get('TOKEN','')


def mint_and_upload(file_loc,name,comp_id):
    meta = {
        'name':name,
        EVI_PREFIX + "generatedBy":{'@id':comp_id},
        'namespace':NS,
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
    r = requests.post(url,files=files,headers = {"Authorization": TOKEN})
    print(r.content.decode())
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
    r = requests.put(ORS_URL + job_id,data = json.dumps(meta),headers = {"Authorization": TOKEN})
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
            minted = mint_and_upload(file_loc,name,'ark:' + NS + '/' + JOBID)
            already_minted[file_loc] = minted
            supported_ids.append(minted)

for file in already_minted:
    if already_minted[file] in supported_ids or already_minted[file] in data_ids:
        continue
    else:
        supported_ids.append(already_minted[file])

with open('/meta/inputs.json', 'w') as outfile:
    json.dump(already_minted, outfile)

id_dict = mint_and_upload('/meta/inputs.json',"Job outputs for " + str('ark:' + NS + '/' + JOBID),'ark:' + NS + '/' + JOBID)
id_dict = mint_and_upload('/meta/output_ids.json',"Nipype outputs for " + str('ark:' + NS + '/' + JOBID),'ark:' + NS + '/' + JOBID)
update_job_id('ark:' + NS + '/' + JOBID,supported_ids,id_dict)

import os
import sys
import requests
import json

TRANSFER_URL = os.environ.get("TRANSFER_URL","http://transfer/")
TOKEN =  os.environ.get('TOKEN','')

ORS_URL = os.environ.get("ORS_URL","http://mds.ors/")


def get_dist_ids(id):
    if isinstance(id,list):
        dist_ids = []
        file_names = []
        for i in id:
            if i == '':
                continue
            current_id, file_name = get_dist_ids(i)
            dist_ids.append(current_id)
            file_names.append(file_name)
        return dist_ids,file_names

    r = requests.get(ORS_URL + id,headers = {"Authorization": TOKEN})

    data_dict = r.json()
    if isinstance(data_dict['distribution'],list):
        if data_dict['distribution'][-1].get('@type','') == 'DataDownload':
            data_url = data_dict['distribution'][-1]['contentUrl']
            file_name = data_url.split('/')[-1]
            dist_id = data_dict['distribution'][-1]['@id']
        else:
            dist_r = requests.get(ORS_URL + data_dict['distribution'][-1]['@id'])
            data_url = dist_r.json()['name']
            file_name = data_url.split('/')[-1]
            dist_id = data_dict['distribution'][-1]['@id']
    else:
        if data_dict['distribution'].get('@type','') == 'DataDownload':
            data_url = data_dict['distribution']['contentUrl']
            file_name = data_url.split('/')[-1]
            dist_id = data_dict['distribution']['@id']
        else:
            dist_r = requests.get(ORS_URL + data_dict['distribution']['@id'])
            data_url = dist_r.json()['name']
            file_name = data_url.split('/')[-1]
            dist_id = data_dict['distribution']['@id']
    return dist_id, file_name


def download_all(dist_ids,names,data_ids):
    ids = {}
    for i in range(len(dist_ids)):
        r = requests.get(TRANSFER_URL + 'data/' + dist_ids[i],headers = {"Authorization": TOKEN})
        data = r.content
        with open('/data/' + names[i], 'wb') as file_data:
            file_data.write(data)
        ids['/data/' +  names[i]] = data_ids[i]
    return ids

def download_script(dist_ids,names):
    for i in range(len(dist_ids)):
        r = requests.get(TRANSFER_URL + 'data/' + dist_ids[i],headers = {"Authorization": TOKEN})
        data = r.content
        with open('/data/' + names[i], 'wb') as file_data:
            file_data.write(data)

while True:
    try:
        data_ids = os.environ.get("DATA")
        data_ids = data_ids.replace('[','').replace(']','').split(',')
        dist_ids, names = get_dist_ids(data_ids)
        ids = download_all(dist_ids,names,data_ids)
        with open('/meta/inputs.json', 'w') as outfile:
            json.dump(ids, outfile)
        with open('/meta/outputs.json', 'w') as outfile:
            json.dump(ids, outfile)
        break
    except:
        f = open('/dev/termination-log','w')
        f.write('Downloading Data Failed.')
        raise Exception
while True:

    script_ids = os.environ.get("SCRIPT")
    script_ids = script_ids.replace('[','').replace(']','').split(',')
    dist_ids, names = get_dist_ids(script_ids)
    download_script(dist_ids,names)
    break

    f = open('/dev/termination-log','w')
    f.write('Downloading Script Failed.')
    raise Exception

import requests
import time
import os
import json
from datetime import datetime
import random
import string
import yaml
import kubernetes as k
import minio

MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')
EVI_PREFIX = 'evi:'
ORS_URL = os.environ.get("ORS_URL","ors.uvadco.io/")


def build_eg(job_id):

    r = requests.get('http://eg/eg/' + job_id)

    if 'error' in r.json().keys():
        return False

    return True
def gather_inputs(request):
    '''
    Gathers inputs from request
    '''

    if request.data == b'':

        return False, "Please POST json with keys, Dataset Identifier,\
                Job Identifier, and Main Function"
        (jsonify({'error':"Please POST json with keys, Dataset Identifier,\
                Job Identifier, and Main Function",'valid':False}))

    try:

        inputs = json.loads(request.data.decode('utf-8'))

    except:

        return False,"Please POST JSON file"
        (jsonify({'error':"Please POST JSON file",'valid':False}))

    return True, inputs

def pod_running(pod_name):
    '''
    checks whether pod for given job is Running
    '''

    k.config.load_incluster_config()
    v1 = k.client.CoreV1Api()

    namespace = "default"

    try:

        pod_info = v1.read_namespaced_pod_status(pod_name,namespace,
                        pretty = True)

        status = pod_info._status.phase

        if status == 'Running' or status == 'Pending':

            return True

        return False

    except:

        return False

def find_pod(pod_name):
    '''
    checks whether pod for given job is Running
    '''

    k.config.load_incluster_config()
    v1 = k.client.CoreV1Api()


    namespace = "default"

    try:

        pod_info = v1.read_namespaced_pod_status(pod_name,namespace,
                        pretty = True)

    except:

        return False

    return True

def get_pod_status(pod_name):
    '''
    Gets pod logs for job pod
    '''

    k.config.load_incluster_config()

    v1 = k.client.CoreV1Api()


    namespace = "default"
    pod_info = v1.read_namespaced_pod_status(pod_name,namespace,
                    pretty = True)

    status = pod_info._status.phase

    return status

def get_pod_logs(pod_name):
    '''
    Gets pod logs for job pod
    '''

    k.config.load_incluster_config()

    v1 = k.client.CoreV1Api()


    namespace = "default"

    pod_logs = v1.read_namespaced_pod_log(pod_name,namespace,container=pod_name,pretty = True)

    pod_info = v1.read_namespaced_pod_status(pod_name,namespace,
                    pretty = True)

    status = pod_info._status.phase

    if status == 'Failed' and pod_logs == '':
        pod_logs = 'Command Unrecognized.'


    # except:
    #
    #     return "error", "Couldn't get logs does pod exist?"

    return pod_logs

def whyd_pod_fail(pod_name):
    '''
    Determines at which point the pod faield
    '''

    k.config.load_incluster_config()

    v1 = k.client.CoreV1Api()

    pod = v1.read_namespaced_pod('pod-name','default')

    #If only first initContainer ran then data download failed
    if len(pod.status.init_container_statuses) == 1:
        failed_container = 'Download'
        message =  pod.status.init_container_statuses[0].state.terminated.message

    #kubernetes labels last successful initContainer ready
    #so if there's 2 initContainers and second is ready that
    #means job completed and write failed
    elif status.container_statuses[1].ready == True:
        failed_container = 'WriteOutputs'
        message = pod.status.message

    else:
        failed_container = 'JobRunner'
        message = pod.status.init_container_statuses[1].state.terminated.message

    return failed_container, message


def gather_job_outputs(job_id,bucket,rest):
    '''
    Looks in the job folder in minio and finds all
    outputs of the computation
    '''
    minioClient = minio.Minio(MINIO_URL,
                    access_key=MINIO_ACCESS_KEY,
                    secret_key=MINIO_SECRET,
                    secure=False)
    print(bucket)
    print(rest)
    objects = minioClient.list_objects(bucket, prefix= rest + job_id,
                                        recursive = True)

    outputs = []
    for obj in objects:
        outputs.append(obj.object_name)

    return outputs
import random
import string

def random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

def mint_output_ids(outputs,job_id,ns,qualifer = False):
    '''
    Mints Identifiers for all outputs of the
    computation
    '''

    all_minted = True
    output_ids = []
    for output in outputs:

        file_name = output.split('/')[-1]
        file_format = file_name.split('.')[-1]

        dist_meta = {
            "@type":"DataDownload",
            "name":file_name,
            "fileFormat":file_format,
            "contentUrl":MINIO_URL + '/breakfast/' + output
        }

        if qualifer:
            url = ORS_URL + "ark:"  + ns + '/' + qualifier + '/' + random_alphanumeric_string(30)
        url = ORS_URL + "shoulder/ark:"  + ns

        r = requests.post(url,data = json.dumps(dist_meta))

        returned = r.json()

        if 'created' in returned:
            dist_meta['@id'] = returned['created']

        else:
            output_ids.append({'error':'Failed minting id for ' + str(output)})
            all_minted = False
            continue

        meta = {
            "name":file_name,
            "@type":"Dataset",
            EVI_PREFIX + "generatedBy":{'@id':job_id},
            "distribution":[dist_meta]
        }

        r = requests.post(ORS_URL + "shoulder/ark:" + ns,data = json.dumps(meta))

        returned = r.json()

        if 'created' in returned:

            output_ids.append(returned['created'])

        else:
            output_ids.append({'error':'Failed minting id for ' + str(output)})
            all_minted = False

    return output_ids, all_minted

def update_job_id(job_id,job_status,logs,output_ids):
    '''
    Updates Job Identifier to show completion or
    failure of job
    '''
    if output_ids == []:
        meta = {
            "status":job_status,
            "logs":logs,
            'emdTime':time.time()
        }
        r = requests.put(ORS_URL + job_id,data = json.dumps(meta))
        return

    id_outputs = []
    for id in output_ids:
        id_outputs.append({"@id":id})

    meta = {
        "status":job_status,
        "logs":logs,
        'ended':time.time(),
        EVI_PREFIX + 'supports':id_outputs
    }
    print(output_ids)
    r = requests.put(ORS_URL + job_id,data = json.dumps(meta))
    return

def clean_up_pods(pod_name):
    '''
    Removes completed Pod and Service
    '''

    k.config.load_incluster_config()
    v1 = k.client.CoreV1Api()


    service_name = pod_name
    namespace = "default"


    delete_pop = v1.delete_namespaced_pod(pod_name,namespace)
    delete_service = v1.delete_namespaced_service(service_name,namespace)

    return

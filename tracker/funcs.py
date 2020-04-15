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

ORS_URL = os.environ.get("ORS_URL","ors.uvadco.io/")

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

def get_pod_logs(pod_name):
    '''
    Gets pod logs for job pod
    '''

    k.config.load_incluster_config()

    v1 = k.client.CoreV1Api()


    namespace = "default"

    pod_logs = v1.read_namespaced_pod_log(pod_name,namespace,
                    pretty = True)

    pod_info = v1.read_namespaced_pod_status(pod_name,namespace,
                    pretty = True)

    status = pod_info._status.phase

    # except:
    #
    #     return "error", "Couldn't get logs does pod exist?"

    return status, pod_logs

def gather_job_outputs(job_id):

    minioClient = minio.Minio(MINIO_URL,
                    access_key=MINIO_ACCESS_KEY,
                    secret_key=MINIO_SECRET,
                    secure=False)

    objects = minioClient.list_objects('breakfast', prefix=job_id,
                                        recursive = True)

    outputs = []
    for obj in objects:
        outputs.append(obj.object_name)

    return outputs

def mint_output_ids(outputs,job_id):

    output_ids = []
    for output in outputs:

        file_name = output.split('/')[-1]
        file_format = file_name.split('.')[-1]

        meta = {
            "name":file_name,
            "evi:generatedBy":job_id,
            "distribution":[{
                "@type":"DataDownload",
                "name":file_name,
                "fileFormat":file_format,
                "contentURL":MINIO_URL + output
            }]
        }

        r = requests.post(ORS_URL + + "shoulder/ark:99999",data = json.dumps(meta))

        returned = r.json()

        if 'created' in returned:

            output_ids.append(returned['id'])

    return output_ids

def update_job_id(job_id,job_status,logs):
    '''
    Updates Job Identifier to show completion or
    failure of job
    '''

    pass

def clean_up_pods(job_id):
    '''
    Removes completed Pod and Service
    '''

    k.config.load_incluster_config()
    v1 = k.client.CoreV1Api()

    pod_name = "sparkjob-" + job_id
    service_name = "sparkjob-" + job_id
    namespace = "default"

    try:

        delete_pop = v1.delete_namespaced_pod(pod_name,namespace)
        delete_service = v1.delete_namespaced_service(service_name,namespace)

    except:

        return False

    return True

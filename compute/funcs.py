#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import requests, logging
import time
import os
from datetime import datetime
import random
import string
import yaml
import kubernetes as k
import json
from werkzeug.routing import PathConverter

MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')

ORS_URL = os.environ.get("ORS_URL","ors.uvadco.io/")
EVI_PREFIX = 'evi:'
class EverythingConverter(PathConverter):
    regex = '.*?'

def get_job_status(ark,token):

    r = requests.get(ORS_URL + ark,headers = {"Authorization": token})

    meta = r.json()

    status = meta['status']

    return status

def parse_request(request):

    success, inputs = gather_inputs(request)

    if not success:

        return False,'','','Post json with keys datasetID and scriptID'

    try:

        data_id = inputs['datasetID']

    except:

        return False,'','','JSON missing required key datasetID'

    try:

        script_id = inputs['scriptID']

    except:

        return False,'','','JSON missing required key scriptID'

    return True, data_id,script_id,''
import random
import string
def random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

def get_distribution(id,token):
    """Validates that given identifier exists in Mongo.
        Returns location in minio. """

    if isinstance(id,list):

        locations = []
        for i in id:
            success, location = get_distribution(i,token)

            if success:
                locations.append(location)
            else:
                return False, str(i) + ' ' +location

        return True, locations

    r = requests.get(ORS_URL + id,headers = {"Authorization": token})

    if r.status_code != 200:

        return False, "Identifier Doesn't Exist."

    try:

        data_dict = r.json()
        print(data_dict)
        if isinstance(data_dict['distribution'],list):
            data_url = data_dict['distribution'][0]['contentUrl']
        else:
            data_url = data_dict['distribution']['contentUrl']
        file_location = '/'.join(data_url.split('/')[1:])

    except:
        print(id)
        return False, "Distribution not found. Or distribution formatting different than expected."

    return True, file_location

def get_docker_image(id,token):
    """Validates that given identifier exists in Mongo.
        Returns location in minio. """

    r = requests.get(ORS_URL + id,headers = {"Authorization": token})

    if r.status_code != 200:

        return False, "Identifier Doesn't Exist."

    try:

        data_dict = r.json()

        docker_image = data_dict['image']


    except:

        return False, "image tag not found in metadata."

    return True, docker_image

def track(job):

    job_id = job.job_id
    prefix = job.prefix
    job_type = job.job_type
    ns = job.namespace

    track = {
            'job_id':job_id,
            'output_location':prefix,
            'job_type':job_type,
            'namespace':ns,
            'qualifer':job.qualifer,
            'token':job.token
            }

    r = requests.post('http://localhost:5001/track',json = track)

    if r.status_code != 200:

        return r.status_code

    return r.content.decode()

def nitrack(job):

    job_id = job.job_id
    prefix = job.prefix
    job_type = job.job_type
    ns = job.namespace

    track = {
            'job_id':job_id,
            'output_location':prefix,
            'job_type':job_type,
            'namespace':job.namespace,
            'token':job.token
            }

    r = requests.post('http://localhost:5001/nitrack',json = track)

    if r.status_code != 200:

        return r.status_code

    return r.content.decode()

def mint_ouput_ids(job_id):

    pass

def delete_service(service_name):
    '''
    Removes completed Pod and Service
    '''

    k.config.load_incluster_config()
    v1 = k.client.CoreV1Api()


    namespace = "default"

    try:

        delete_service = v1.delete_namespaced_service(service_name,namespace)

    except:

        return False

    return True

def delete_pod(pod_name):
    '''
    Removes Pod
    '''

    k.config.load_incluster_config()
    v1 = k.client.CoreV1Api()


    namespace = "default"

    try:

        delete_service = v1.delete_namespaced_pod(pod_name,namespace)

    except:

        return False

    return True

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

def create_service(service_def):

    k.config.load_incluster_config()

    v1 = k.client.CoreV1Api()


    resp = v1.create_namespaced_service(body = service_def,
                                        namespace="default")

    return resp


def create_pod(pod_def):

    k.config.load_incluster_config()
    v1 = k.client.CoreV1Api()

    resp = v1.create_namespaced_pod(body = pod_def,
                                    namespace="default")

    return resp

# def update_pod_service_yaml(data_location,script_location,job_id):
#
#     with open("./yamls/pod.yaml") as f:
#
#         pod = yaml.safe_load(f)
#
#     with open("./yamls/service.yaml") as f:
#
#         service = yaml.safe_load(f)
#
#     service['metadata']['name'] = "sparkjob-" + job_id
#
#     service['spec']['selector']['app'] = "sparkjob-" + job_id
#
#     pod['metadata']['name'] = "sparkjob-" + job_id
#
#     pod['spec']['containers'][0]['name'] = "sparkjob-" + job_id
#
#     pod['metadata']['labels']['app'] = "sparkjob-" + job_id
#
#     pod['spec']['containers'][0]['command'].append("--conf")
#
#     pod['spec']['containers'][0]['command'].append("spark.hadoop.fs.s3a.endpoint=" + MINIO_URL)
#
#     pod['spec']['containers'][0]['command'].append("--conf")
#
#     pod['spec']['containers'][0]['command'].append("spark.hadoop.fs.s3a.access.key=" + MINIO_ACCESS_KEY)
#
#     pod['spec']['containers'][0]['command'].append("--conf")
#
#     pod['spec']['containers'][0]['command'].append("spark.hadoop.fs.s3a.secret.key=" + MINIO_SECRET)
#
#     pod['spec']['containers'][0]['command'].append(script_location)
#
#     pod['spec']['containers'][0]['command'].append(data_location)
#
#     pod['spec']['containers'][0]['command'].append(job_id)
#
#     return pod, service

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def gather_inputs(request):

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

def get_running_jobs():
    '''
    gathers all running jobs returns list
    of pod names
    '''

    k.config.load_incluster_config()
    v1 = k.client.CoreV1Api()

    pods = v1.list_namespaced_pod('default', pretty=True)

    active_jobs = []
    for pod in pods.items:

        pod_name = pod.metadata.name
        if 'sparkjob-' in pod_name:
            active_jobs.append(pod_name)#.replace('sparkjob-',''))
        if 'custom-' in pod_name:
            active_jobs.append(pod_name)#.replace('sparkjob-',''))
        if 'nipype-' in pod_name:
            active_jobs.append(pod_name)#.replace('sparkjob-',''))

    return active_jobs

def list_services():
    '''
    List all services on kubernetes
    '''

    k.config.load_incluster_config()
    v1 = k.client.CoreV1Api()

    services = v1.list_namespaced_service('default', pretty=True)

    list_services = []
    for service in services.items:

        service_name = service.metadata.name

        list_services.append(service_name)

    return list_services

def list_pods():
    '''
    List all pods on kubernetes
    '''

    k.config.load_incluster_config()
    v1 = k.client.CoreV1Api()

    pods = v1.list_namespaced_pod('default', pretty=True)

    list_pods = []
    for pod in pods.items:

        pod_name = pod.metadata.name

        list_pods.append(pod_name)

    return list_pods

def validate_input(id):
    """Validates that given identifier exists in Mongo.
        Returns location in minio. """
    r = requests.get(ORS_URL + datasetid)

    if r.status_code != 200:

        return False, "Identifier Doesn't Exist."

    try:

        data_dict = r.json()

        data_url = data_dict['distribution'][0]['contentUrl']

        file_location = '/'.join(data_url.split('/')[1:])

    except:

        return False, "Distribution not found. Or distribution formatting different than expected."

    return True, file_location

def mint_job_id(data_id,script_id):

    return True, randomString(10)

    base_meta = {
        "@type":EVI_PREFIX  + "Computation",
        "began":datetime.fromtimestamp(time.time()).strftime("%A, %B %d, %Y %I:%M:%S"),
        EVI_PREFIX + "usedDataset":data_id,
        EVI_PREFIX + "usedSoftware":script_id
    }

    url = ORS_URL + "shoulder/ark:99999"

    r = requests.post(url, data=json.dumps(base_meta))
    returned = r.json()

    if 'created' in returned:

        return True, returned['id']

    return False, 0

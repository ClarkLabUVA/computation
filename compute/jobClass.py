import requests, yaml, json
import kubernetes as k
from funcs import *

MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')

ORS_URL = os.environ.get("ORS_URL","ors.uvadco.io/")

class Job:

    def __init__(self, request,custom_container = False):

        self.correct_inputs, self.dataset_ids, self.script_id,self.error = parse_request(request)
        self.custom_container = custom_container

        if not isinstance(self.dataset_ids,list):
            self.dataset_ids = [self.dataset_ids]


        if self.correct_inputs:
            _, inputs = gather_inputs(request)

            if custom_container:
                if 'containerID' in inputs.keys():
                    self.container_id = inputs['containerID']
                    try:
                        self.command = inputs['command']
                    except:
                        self.command = 'python3'
                    success, self.container_image = get_docker_image(self.container_id)
                    if not success:
                        self.correct_inputs = False
                        self.error = self.container_image
                else:
                    self.correct_inputs = False
                    self.error = 'Missing required input containerID'

            if 'prefix' in inputs.keys():
                self.prefix = inputs['prefix']
            else:
                self.prefix = 'breakfast/'

            if 'executor-memory' in inputs.keys():
                self.executor_memory = inputs['executor-memory']
            else:
                self.executor_memory = '5g'

            if 'executors' in inputs.keys():
                self.executors = inputs['executors']
            else:
                self.executors = '1'

            real_data_ids, self.data_locations = get_distribution(self.dataset_ids)
            real_script_id, self.script_location = get_distribution(self.script_id)

            if not real_data_ids:

                self.correct_inputs = False
                self.error = self.data_locations

            if not real_script_id:

                self.correct_inputs = False
                self.error = self.script_location


    def mint_job_id(self):

        datasets = []
        for id in self.dataset_ids:
            datasets.append({'@id':id})

        base_meta = {
            "@type":"eg:Computation",
            "began":datetime.fromtimestamp(time.time()).strftime("%A, %B %d, %Y %I:%M:%S"),
            "eg:usedDataset":datasets,
            "eg:usedSoftware":{'@id':self.script_id},
            "status":'Running'
        }

        if self.custom_container:
            base_meta['eg:usedSoftware'] = [{'@id':self.script_id},
                                            {'@id':self.container_id}]

        url = ORS_URL + "shoulder/ark:99999"

        r = requests.post(url, data=json.dumps(base_meta))
        returned = r.json()

        if 'created' in returned:

            self.job_id = returned['created'].split('/')[1]
            return True

        return False

    def create_nipype_defs(self):

        with open("./yamls/ni_pod.yaml") as f:

            self.pod = yaml.safe_load(f)

        str_datasetids = ''
        for id in self.dataset_ids:
            str_datasetids = str_datasetids + id + ','

        self.pod_name = "sparkjob-" + self.job_id

        self.pod['metadata']['name'] = "sparkjob-" + self.job_id

        self.pod['spec']['containers'][0]['name'] = "sparkjob-" + self.job_id

        self.pod['metadata']['labels']['app'] = "sparkjob-" + self.job_id
        self.pod['spec']['containers'][0]['env'] = []
        self.pod['spec']['containers'][0]['env'].append({'name':'ORS_URL','value':ORS_URL})
        self.pod['spec']['containers'][0]['env'].append({'name':'MINIO_ACCESS_KEY','value':MINIO_ACCESS_KEY})
        self.pod['spec']['containers'][0]['env'].append({'name':'MINIO_URL','value':MINIO_URL})
        self.pod['spec']['containers'][0]['env'].append({'name':'MINIO_SECRET','value':MINIO_SECRET})
        self.pod['spec']['containers'][0]['env'].append({'name':'DATA','value':str_datasetids})
        self.pod['spec']['containers'][0]['env'].append({'name':'SCRIPT','value':self.script_id})
        self.pod['spec']['containers'][0]['env'].append({'name':'SCRIPTNAME','value':self.script_location.split('/')[-1]})
        self.pod['spec']['containers'][0]['env'].append({'name':'OUTPUT','value':self.prefix + self.job_id})
        self.pod['spec']['containers'][0]['env'].append({'name':'JOBID','value':self.job_id})


        print(self.pod)

    def create_custom_k_defs(self):

        with open("./yamls/custom_job.yaml") as f:

            self.pod = yaml.safe_load(f)

        str_datasetids = ''
        for id in self.dataset_ids:
            str_datasetids = str_datasetids + id + ','

        self.pod_name = "sparkjob-" + self.job_id

        self.pod['metadata']['name'] = "sparkjob-" + self.job_id

        # self.pod['spec']['containers'][0]['name'] = "write_data"
        # self.pod['spec']['containers'][0]['image'] = self.container_image

        self.pod['metadata']['labels']['app'] = "sparkjob-" + self.job_id

        envs = []
        envs.append({'name':'ORS_URL','value':ORS_URL})
        envs.append({'name':'DATA','value':str_datasetids})
        envs.append({'name':'SCRIPT','value':self.script_id})
        envs.append({'name':'SCRIPTNAME','value':self.script_location.split('/')[-1]})
        envs.append({'name':'OUTPUT','value':self.prefix + self.job_id})
        envs.append({'name':'JOBID','value':self.job_id})
        envs.append({'name':'MINIO_SECRET','value':MINIO_SECRET})
        envs.append({'name':'MINIO_ACCESS_KEY','value':MINIO_ACCESS_KEY})
        envs.append({'name':'MINIO_URL','value':MINIO_URL})

        self.pod['spec']['containers'][0]['env'] = envs
        self.pod['spec']['initContainers'][0]['env'] = envs
        self.pod['spec']['initContainers'][1]['env'] = envs

        self.pod['spec']['initContainers'][1]['name'] = "sparkjob-" + self.job_id
        self.pod['spec']['initContainers'][1]['image'] = self.container_image
        self.pod['spec']['initContainers'][1]['command'] = [self.command,"/data/" + self.script_location.split('/')[-1]]


        print(self.pod)

    def create_kubernetes_defs(self):

        with open("./yamls/pod.yaml") as f:

            self.pod = yaml.safe_load(f)

        with open("./yamls/service.yaml") as f:

            self.service = yaml.safe_load(f)

        self.service_name = "sparkjob-" + self.job_id
        self.pod_name = "sparkjob-" + self.job_id

        str_locations = ''
        for id in self.data_locations:
            str_locations = 's3a://' + str_locations + id + ','

        self.service['metadata']['name'] = "sparkjob-" + self.job_id

        self.service['spec']['selector']['app'] = "sparkjob-" + self.job_id

        self.pod['metadata']['name'] = "sparkjob-" + self.job_id

        self.pod['spec']['containers'][0]['name'] = "sparkjob-" + self.job_id

        self.pod['metadata']['labels']['app'] = "sparkjob-" + self.job_id

        self.pod['spec']['containers'][0]['env'] = []
        self.pod['spec']['containers'][0]['env'].append({'name':'ORS_URL','value':ORS_URL})
        self.pod['spec']['containers'][0]['env'].append({'name':'MINIO_ACCESS_KEY','value':MINIO_ACCESS_KEY})
        self.pod['spec']['containers'][0]['env'].append({'name':'MINIO_URL','value':MINIO_URL})
        self.pod['spec']['containers'][0]['env'].append({'name':'MINIO_SECRET','value':MINIO_SECRET})
        self.pod['spec']['containers'][0]['env'].append({'name':'DATA','value':str_locations})
        self.pod['spec']['containers'][0]['env'].append({'name':'OUTPUT','value':self.prefix + self.job_id})

        self.pod['spec']['containers'][0]['command'].append("--conf")
        self.pod['spec']['containers'][0]['command'].append("spark.hadoop.fs.s3a.endpoint=" + MINIO_URL)

        self.pod['spec']['containers'][0]['command'].append("--conf")
        self.pod['spec']['containers'][0]['command'].append("spark.hadoop.fs.s3a.access.key=" + MINIO_ACCESS_KEY)

        self.pod['spec']['containers'][0]['command'].append("--conf")
        self.pod['spec']['containers'][0]['command'].append("spark.hadoop.fs.s3a.secret.key=" + MINIO_SECRET)

        self.pod['spec']['containers'][0]['command'].append("--conf")
        self.pod['spec']['containers'][0]['command'].append('spark.kubernetes.executor.request.cores=' + self.executors)

        self.pod['spec']['containers'][0]['command'].append("--conf")
        self.pod['spec']['containers'][0]['command'].append('spark.executor.memory=' + self.executor_memory)

        self.pod['spec']['containers'][0]['command'].append('s3a://' + self.script_location)

        self.pod['spec']['containers'][0]['command'].append('s3a://' + self.prefix + self.job_id)

        for location in self.data_locations:
            self.pod['spec']['containers'][0]['command'].append('s3a://' + location)



    def delete_id(self):

        url = ORS_URL + self.job_id

        r = requests.delete(url)

        return


    def create_pod(self):

        k.config.load_incluster_config()
        v1 = k.client.CoreV1Api()

        self.pod_resp = v1.create_namespaced_pod(body = self.pod,
                                        namespace="default")

    def create_service(self):

        k.config.load_incluster_config()
        v1 = k.client.CoreV1Api()

        self.service_resp = v1.create_namespaced_service(body = self.service,
                                            namespace="default")

    def delete_pod(self):
        '''
        Removes Pod
        '''

        k.config.load_incluster_config()
        v1 = k.client.CoreV1Api()

        namespace = "default"

        delete_pod = v1.delete_namespaced_pod(self.pod_name,namespace)

    def delete_service(self):
        '''
        Removes Service
        '''

        k.config.load_incluster_config()
        v1 = k.client.CoreV1Api()

        namespace = "default"

        delete_service = v1.delete_namespaced_service(self.service_name,namespace)

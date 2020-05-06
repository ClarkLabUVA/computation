import requests, yaml, json
import kubernetes as k
from funcs import *

MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')

ORS_URL = os.environ.get("ORS_URL","ors.uvadco.io/")

class Job:

    def __init__(self, request):

        self.correct_inputs, self.dataset_ids, self.script_id,self.error = parse_request(request)
        if not isinstance(self.dataset_ids,list):
            self.dataset_ids = [self.dataset_ids]
        self.script_location = "breakfast/test.py"
        self.data_locations = ["Testingtoseeifthisworks"]

        if self.correct_inputs:
            _, inputs = gather_inputs(request)

            if 'prefix' in inputs.keys():
                self.prefix = inputs['prefix']
            else:
                self.prefix = 'breakfast'

            if 'executor-memory' in inputs.keys():
                self.executor_memory = inputs['executor-memory']
            else:
                self.executor_memory = '5g'

            if 'executors' in inputs.keys():
                self.executors = inputs['executors']
            else:
                self.executor_memory = '1'
        #     real_data_ids, self.data_locations = get_distribution(self.dataset_id)
        #     real_script_id, self.script_location = get_distribution(self.script_id)
        #
        #     if not real_data_ids:
        #
        #         self.correct_inputs = False
        #         self.error = self.data_locations
        #
        #     if not real_script_id:
        #
        #         self.correct_inputs = False
        #         self.error = self.script_location


    def mint_job_id(self):

        self.job_id = randomString(10)
        return True

        base_meta = {
            "@type":"eg:Computation",
            "began":datetime.fromtimestamp(time.time()).strftime("%A, %B %d, %Y %I:%M:%S"),
            "eg:usedDataset":self.dataset_ids,
            "eg:usedSoftware":self.script_id,
            "status":'Running'
        }

        url = ORS_URL + "shoulder/ark:99999"

        r = requests.post(url, data=json.dumps(base_meta))
        returned = r.json()

        if 'created' in returned:

            self.job_id = returned['id']
            return True

        return False

    def create_kubernetes_defs(self):

        with open("./yamls/pod.yaml") as f:

            self.pod = yaml.safe_load(f)

        with open("./yamls/service.yaml") as f:

            self.service = yaml.safe_load(f)

        self.service_name = "sparkjob-" + self.job_id
        self.pod_name = "sparkjob-" + self.job_id

        self.service['metadata']['name'] = "sparkjob-" + self.job_id

        self.service['spec']['selector']['app'] = "sparkjob-" + self.job_id

        self.pod['metadata']['name'] = "sparkjob-" + self.job_id

        self.pod['spec']['containers'][0]['name'] = "sparkjob-" + self.job_id

        self.pod['metadata']['labels']['app'] = "sparkjob-" + self.job_id

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



    def delete_id():

        pass

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

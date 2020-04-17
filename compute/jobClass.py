import requests, yaml, json
import kubernetes as k
from funcs import *

class Job:

    def __init__(self, request):

        self.correct_inputs, self.dataset_id, self.script_id,self.error = parse_request(request)
        self.script_location = "s3a://breakfast/test.py"
        self.data_location = "Testingtoseeifthisworks"
        # if self.correct_inputs:
        #
        #     real_data_id, self.data_location = get_distribution(self.dataset_id)
        #     real_script_id, self.script_location = get_distribution(self.script_id)
        #
        #     if not real_data_idata:
        #
        #         self.correct_inputs = False
        #         self.error = self.data_location
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
            "eg:usedDataset":data_id,
            "eg:usedSoftware":script_id
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

        self.pod['spec']['containers'][0]['command'].append(self.script_location)

        self.pod['spec']['containers'][0]['command'].append(self.data_location)

        self.pod['spec']['containers'][0]['command'].append(self.job_id)

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

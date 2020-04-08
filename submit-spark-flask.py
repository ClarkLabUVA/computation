import requests
import json
import sys
import random
from datetime import datetime
import pandas as pd
from minio import Minio
import os
import time
import warnings
import stardog
from flask import Flask, render_template, request, redirect,jsonify



def build_evidence_graph(data,clean = True):
    eg = {}
    context = {'http://www.w3.org/1999/02/22-rdf-syntax-ns#':'@',
          'http://schema.org/':'',
           'http://example.org/':'eg:',
           "https://wf4ever.github.io/ro/2016-01-28/wfdesc/":'wfdesc:'
          }
    trail = []

    for index, row in data.iterrows():
        if pd.isna(row['x']):
            trail = []
            continue
        if clean:
            for key in context:

                if key in row['p']:
                    row['p'] = row['p'].replace(key,context[key])
                if key in row['y']:
                    row['y'] = row['y'].replace(key,context[key])

        if '@id' not in eg.keys():
            eg['@id'] = row['x']

        if trail == []:
            if row['p'] not in eg.keys():
                eg[row['p']] = row['y']
            else:
                trail.append(row['p'])
                if not isinstance(eg[row['p']],dict):
                    eg[row['p']] = {'@id':row['y']}

            continue
        current = eg
        for t in trail:
            current = current[t]
        if row['p'] not in current.keys():
                current[row['p']] = row['y']
        else:
            trail.append(row['p'])
            if not isinstance(current[row['p']],dict):
                current[row['p']] = {'@id':row['y']}
    return eg
def stardog_eg_csv(ark):
    conn_details = {
        'endpoint': 'http://stardog.uvadcos.io',
        'username': 'admin',
        'password': 'admin'
    }
    with stardog.Connection('db', **conn_details) as conn:
        conn.begin()
    #results = conn.select('select * { ?a ?p ?o }')
        results = conn.paths("PATHS START ?x=<"+ ark + "> END ?y VIA ?p",content_type='text/csv')
    with open('/star/test.csv','wb') as f:
        f.write(results)

    return

def make_eg(ark):

    stardog_eg_csv(ark)

    data = pd.read_csv('/star/test.csv')

    eg = build_evidence_graph(data)

    clean_up()

    return eg

def create_named_graph(meta,id):

    with open('/star/meta.json','w') as f:

        json.dump(meta, f)

    conn_details = {
        'endpoint': 'http://stardog.uvadcos.io',
        'username': 'admin',
        'password': 'admin'
    }

    with stardog.Connection('db', **conn_details) as conn:

        conn.begin()

        conn.add(stardog.content.File("/star/meta.json"))#,graph_uri='http://ors.uvadcos/'+id)

        conn.commit()

    # cmd = 'stardog data add --named-graph http://ors.uvadcos.io/' + id + ' -f JSONLD test "/star/meta.json"'
    # test = os.system(cmd)
    # warnings.warn('Creating named graph returned: ' + str(test))

    return

def clean_up():

    os.system('rm /star/*')


def download_script(bukcet,location):

    minioClient = Minio('minionas.int.uvadcos.io',
                    access_key='breakfast',
                    secret_key='breakfast',
                    secure=False)

    data = minioClient.get_object("breakfast", location)

    file_name = location.split('/')[-1]

    with open(file_name, 'wb') as file_data:

            for d in data.stream(32*1024):
                file_data.write(d)

    return

def get_dependencies(folder):
    minioClient = Minio('minionas.int.uvadcos.io',
                    access_key='breakfast',
                    secret_key='breakfast',
                    secure=False)

    objects = minioClient.list_objects('breakfast',
                              recursive=True)
    files = []
    for obj in objects:
        name = obj.object_name
        if folder in name:
            files.append(name)
    return files

def get_outputs(job_bucket):

    minioClient = Minio('minionas.int.uvadcos.io',
                    access_key='breakfast',
                    secret_key='breakfast',
                    secure=False)

    objects = minioClient.list_objects('breakfast',
                              recursive=True)
    outputs = []

    for obj in objects:

        if job_bucket in obj.object_name:

            outputs.append([obj.object_name,obj.size])

    return outputs

app = Flask(__name__)

@app.route('/')
def homepage():

    #if more metadata is required add to metadata.html in templates
    return 'hi'
@app.route('/run-job',methods = ['POST'])
def run_job():
    if request.data == b'':
        return(jsonify({'error':"Please POST json with keys, Dataset Identifier, Job Identifier, and Main Function",'valid':False}))

    try:
        inputs = json.loads(request.data.decode('utf-8'))
    except:
        return(jsonify({'error':"Please POST JSON file",'valid':False}))

    datasetid = inputs['Dataset Identifier']
    wfid = inputs['Job Identifier']

    if 'Main Function' in inputs.keys():
        main = inputs['Main Function']
    else:
        main = 'asasdasdasdadaasdadasdads'
    if 'metadata' in inputs.keys():
        given_metadata = inputs['metadata']
    else:
        given_metadata = {}
    if '@type' in given_metadata.keys():
        out_type = given_metadata['@type']
    else:
        out_type = 'Dataset'
    if 'description' in given_metadata.keys():
        out_desc = given_metadata['description']
    else:
        out_desc = ''



    r = requests.get('http://ors.uvadcos.io/' + datasetid)

    if r.status_code != 200:
        raise Exception('Dataset Identifier not Found')

    data_dict = r.json()
    data_url = data_dict['distribution'][0]['contentUrl']
    file_location = '/'.join(data_url.split('/')[1:])

    py_files = []

    r = requests.get('http://ors.uvadcos.io/' + wfid)

    if r.status_code != 200:
        raise Exception('Source Code Identifier not Found')

    source_code_dict = r.json()

    for file in source_code_dict['distribution']:

        py_url = file['contentUrl']
        py_bucket = py_url.split('/')[1]
        py_location = '/'.join(py_url.split('/')[2:])
        py_folder = '/'.join(py_location.split('/')[:-1])
        py_full = '/'.join(py_url.split('/')[1:])

        if main in py_full or len(source_code_dict['distribution']) == 1:

            main = py_full.split('/')[-1]
            found = True
        else:
            main = py_full.split('/')[-1]
            found = True

        download_script(py_bucket,py_location)

        py_files.append(py_full)

    if py_folder[0] == '/':
        py_folder = py_folder[1:]

    dependencies = get_dependencies(py_folder)

    for dependency in dependencies:
        download_script(py_bucket,dependency)

    if not found:

        raise Exception("Please give main file to run")


    job_bucket = 'Job ' + str(random.randint(0,10000))
    if 'name' in given_metadata.keys():
        out_name = given_metadata['name']
    else:
        out_name = 'Output from job ' + job_bucket

    my_cmd = my_cmd = 'spark-submit ' + main + ' "' + file_location + '" "' + job_bucket + '"'

    start_time = datetime.fromtimestamp(time.time()).strftime("%A, %B %d, %Y %I:%M:%S")

    result = os.system(my_cmd)

    end_time = datetime.fromtimestamp(time.time()).strftime("%A, %B %d, %Y %I:%M:%S")





    if result == 0:

        job_meta = {
                    "@context":{
                        '@vocab':"http://schema.org/",
                        'eg':'http://example.org/'
                    },
                    "@type":'eg:Computation',
                    "dateStarted":start_time,
                    "dateEnded":end_time,
                    "eg:usedDataset":{"@id":datasetid},
                    "eg:usedSoftware":{"@id":wfid}
        }

        url = 'http://ors.uvadcos.io/shoulder/ark:99999'

        r = requests.post(url, data=json.dumps(job_meta))
        metareturned = r.json()

        if 'created' in metareturned:

            job_id = metareturned['created']
            job_meta['@id'] = job_id
            #job_meta.pop('@context', None)

            create_named_graph(job_meta,job_id)

            job_eg = make_eg(job_id)

            r = requests.post(url, data=json.dumps({'eg:evidenceGraph':job_eg}))


            outputs_created = get_outputs(job_bucket)

            out_meta = {
                        "@context":{
                            '@vocab':"http://schema.org/",
                            'eg':'http://example.org/'
                        },
                        "@type":out_type,
                        "name":out_name,
                        "description":out_desc,
                        "eg:generatedBy":{'@id':job_id},
                        'distribution':[]
            }
            output_ids = []

            for out in outputs_created:

                file_meta = out_meta


                file = out[0].split('/')[-1]

                file_meta['distribution'] = []

                file_meta['distribution'].append({
                    "@type":"DataDownload",
                    "name":file,
                    'contentSize':out[1],
                    "fileFormat":file.split('.')[-1],
                    "contentUrl":'minionas.uvadcos.io/breakfast/' + out[0]
                })

                r = requests.post(url, data=json.dumps(file_meta['distribution'][0]))

                download_id = r.json()['created']

                file_meta['distribution'][0]['@id'] = download_id

                r = requests.post(url, data=json.dumps(file_meta))

                metareturned = r.json()

                if 'created' in metareturned.keys():

                    output_ids.append(metareturned['created'])

                    file_meta['@id'] = metareturned['created']

                    create_named_graph(file_meta,metareturned['created'])

                    file_eg = make_eg(metareturned['created'])

                    r = requests.put('http://ors.uvadcos.io/' +
                        metareturned['created'] ,
                        data=json.dumps({'eg:evidenceGraph':file_eg}))



            if len(output_ids) > 0 :

                return jsonify({'Job Status':'FINISHED',
                                'Job Identifier':job_id,
                                'Output Identifiers':output_ids,
                                'output location':'minionas.uvadcos.io/breakfast/' + job_bucket})

            else:

                return jsonify({'Job Status':'FINISHED',
                                'Job Identifier':job_id,
                                'Output Identifier':'Posting output metadata failed',
                                'output location':'minionas.uvadcos.io/breakfast/' + job_bucket})

        else:
            return jsonify({'Job Status':'FINISHED',
                            'Job Identifier':'Failed to post job metadata to ors',
                            'Output Identifier':'Posting output metadata failed',
                            'output location':'minionas.uvadcos.io/breakfast/' + job_bucket})
    else:
        return jsonify({'Job Status':'FAILED'})


if __name__ == "__main__":
    app.run(host='0.0.0.0')

#clarklabspark-master.marathon.l4lb.thisdcos.directory:7077

#spark_url = 'http://d-172-25-77-160.dhcp.virginia.edu:6066/v1/submissions/create'





# payload = {
#     "action":"CreateSubmissionRequest",
#     "clientSparkVersion":"2.3.3",
#     "environmentVariables":{
#         "SPARK_ENV_LOADED":"1"
#     },
#     "mainClass":"org.apache.spark.deploy.SparkSubmit",
#     "sparkProperties":{
#         "spark.driver.supervise":"false",
#         "spark.app.name":"Simple App",
#         "spark.eventLog.enabled":"true",
#         "spark.submit.deployMode":"cluster",
#         #"spark.master":"spark://d-172-25-77-160.dhcp.virginia.edu:7077",
#         "sparkmaster":"spark://clarklabspark-master.marathon.l4lb.thisdcos.directory:7077",
#         "spark.py-files":py_files
#     },
#     "appArgs":[file_location,job_bucket],
#     #"appResource":"/Users/justinniestroy-admin/Documents/Work/Tests/Spark/dependencies/sparktest.py",
#     "appResource":main,
# }


# r = requests.post(spark_url, data=json.dumps(payload), headers=headers)
# print(r.content.decode())
#
# curl -X POST http://clarklabspark-master.marathon.l4lb.thisdcos.directory:7077/v1/submissions/create --header "Content-Type:application/json;charset=UTF-8" --data '{
#    "action":"CreateSubmissionRequest",
#    "appArgs":["breakfast/random.csv","test-job2"],
#    "appResource":"sparktest.py",
#    "clientSparkVersion":"2.3.3",
#    "environmentVariables":{
#       "SPARK_ENV_LOADED":"1"
#    },
#    "mainClass":"org.apache.spark.deploy.SparkSubmit",
#    "sparkProperties":{
#       "spark.driver.supervise":"false",
#       "spark.app.name":"Simple App",
#       "spark.eventLog.enabled":"true"
#    }
# }'
# export SPARK_HOME=/spark
# export HADOOP_HOME=/hadoop
# export PATH=$PATH:$SPARK_HOME/bin:$HADOOP_HOME/bin
# export LD_LIBRARY_PATH=$HADOOP_HOME/lib/native
# export PYSPARK_PYTHON=python3
# export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
# export HADOOP_OPTIONAL_TOOLS="hadoop-aws"
# export SPARK_DIST_CLASSPATH=$(hadoop classpath)
#
# pyspark \
#   --executor-memory 4G \
#   --total-executor-cores 4 \
#   --master spark://clarklabspark-master.marathon.l4lb.thisdcos.directory:7077

#my_cmd = 'spark-submit sparktest.py breakfast/random.csv test-job3'
#os.system(my_cmd)

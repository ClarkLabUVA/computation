import requests
import json
import sys
import random
from datetime import datetime
import os
import time
import warnings
from flask import Flask, render_template, request, redirect,jsonify
from funcs import *

MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')

ORS_URL = os.environ.get("ORS_URL","ors.uvadco.io/")

app = Flask(__name__)

@app.route('/')
def homepage():

    return "Status: Working"

@app.route('/test')
def test():

    r = requests.get('http://localhost:5001/')
    return r.content.decode()

@app.route('/track',methods = ['POST','GET'])
def track_job():

    valid, inputs = gather_inputs(request)

    job_id = inputs['job_id']

    r = requests.post('http://localhost:5001/track',json = {'job_id':job_id})

    return r.content.decode()

@app.route('/compute',methods = ['POST','GET'])
def compute():


    valid, inputs = gather_inputs(request)

    if not valid:

        return (jsonify({'error':inputs,'valid':False}))

    data_id = inputs['datasetID']
    script_id = inputs['scriptID']

    #valid_data, data_location = validate_input(data_id)
    #valid_script, script_location = validate_input(script_id)

    valid_data,valid_script = True,True
    script_location = "s3a://breakfast/test.py"
    data_location = "Testingtoseeifthisworks"


    if not ( valid_data and valid_script ):
        return "Identifier not known for one of them"



    success, job_id = mint_job_id(data_id,script_id)

    if not success:
        return "Minting Job ID Failed."


    pod, service = update_pod_service_yaml(data_location,script_location,job_id)


    success = create_service(service)

    if not success:
        delete_job_id(job_id)
        return "failed to make service"


    success = create_pod(pod)

    if not success:
        delete_service(service)
        delete_job_id(job_id)
        return "failed to make pod"

    tracked = track(job_id)

    print(tracked)

    return job_id

if __name__ == "__main__":
    app.run(debug = True)

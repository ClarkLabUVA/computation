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

@app.route('/job',methods = ['POST','GET'])
def compute():


    valid, inputs = gather_inputs(request)

    if not valid:

        return jsonify({'error':inputs,'valid':False}),400

    data_id = inputs['datasetID']
    script_id = inputs['scriptID']

    #valid_data, data_location = validate_input(data_id)
    #valid_script, script_location = validate_input(script_id)

    valid_data,valid_script = True,True
    script_location = "s3a://breakfast/test.py"
    data_location = "Testingtoseeifthisworks"


    if not valid_data:
        return jsonify({'error':'Data ' + data_location}),400
    if not valid_script:
        return jsonify({'error':'Script ' + data_location}),400



    success, job_id = mint_job_id(data_id,script_id)

    if not success:
        return jsonify({'error':'Minting Job Identifier failed'}),503


    pod, service = update_pod_service_yaml(data_location,script_location,job_id)

    success = create_service(service)
    if not success:
        delete_job_id(job_id)

        return jsonify({'error':'Failed to make service.'}),500


    success = create_pod(pod)
    if not success:
        delete_service(job_id)
        delete_job_id(job_id)

        return jsonify({'error':'Failed to make pod.'}),500

    tracked = track(job_id)

    if 'Tracking' not in str(tracked):

        clean_up_pods(job_id)
        delete_job_id(job_id)

        return "failed to track"


    return job_id

if __name__ == "__main__":
    app.run(debug = True)

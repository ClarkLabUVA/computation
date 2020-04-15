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
import threading

MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')
ORS_URL = os.environ.get("ORS_URL","ors.uvadco.io/")

app = Flask(__name__)

@app.route('/')
def homepage():

    return "Tracker: Working"


@app.route('/track',methods = ['POST','GET'])
def add_id_to_track():
    '''
    POST:
        {"job_id":abc1234}
        Tracks given job_id to completion
        Returns True if tracking began sucessfully
        Mints outputs and updates job Identifier as needed
    '''

    valid, inputs = gather_inputs(request)

    track_id = inputs['job_id']

    exists = find_pod('sparkjob-' + track_id)

    if not exists:

        return "No Pod"

    def track(track_id):

        while pod_running('sparkjob-' + track_id):

            print("Tracking: " + track_id)
            time.sleep(30)

        job_status, logs = get_pod_logs('sparkjob-' + track_id)

        print(track_id)
        print("Status: " + job_status)

        outputs = gather_job_outputs(track_id)

        print(outputs)

        #output_ids = mint_output_ids(outputs,job_id)

        success = update_job_id(track_id,job_status,logs)

        clean_up_pods(track_id)

    thread = threading.Thread(target=track, kwargs={'track_id':track_id})
    thread.start()

    return "Tracking " + track_id

if __name__ == "__main__":
    app.run(port = 5001)

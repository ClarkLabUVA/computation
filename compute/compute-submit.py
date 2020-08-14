#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import time,requests,json, sys, random, os, warnings, logging
from datetime import datetime
from flask import Flask, render_template, request, redirect,jsonify
from funcs import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')

ORS_URL = os.environ.get("ORS_URL","ors.uvadco.io/")

app = Flask(__name__)

@app.route('/')
def homepage():

    logger.info('Homepage handling request %s', request)
    return "Status: Working"

@app.route('/job',methods = ['POST','GET'])
def compute():

    logger.info('Job endpoint handling request %s', request)

    if request.method == 'GET':

        running_pods = get_running_pods()

        return jsonify({'runningJobIds':running_pods}),200


    valid, inputs = gather_inputs(request)
    if not valid:

        logger.info('User gave invalid inputs %s', str(inputs))
        return jsonify({'error':inputs,'valid':False}),400


    data_id = inputs['datasetID']
    script_id = inputs['scriptID']

    #valid_data, data_location = validate_input(data_id)
    #valid_script, script_location = validate_input(script_id)

    valid_data,valid_script = True,True
    script_location = "s3a://breakfast/testnotreal.py"
    data_location = "Testingtoseeifthisworks"


    if not valid_data:
        return jsonify({'error':'Data ' + data_location}),400
    if not valid_script:
        return jsonify({'error':'Script ' + data_location}),400



    success, job_id = mint_job_id(data_id,script_id)

    if not success:
        return jsonify({'error':'Minting Job Identifier failed'}),503


    pod, service = update_pod_service_yaml(data_location,script_location,job_id)

    logger.info('Creating Service %s', str(service))
    try:

        s_resp = create_service(service)

    except:

        logger.error('Failed to create service.', exc_info=True)
        delete_job_id(job_id)
        return jsonify({'error':'Failed to make service.'}),500

    logger.info('Creating Pod %s', str(pod))
    try:

        p_resp = create_pod(pod)

    except:

        logger.error('Failed to create pod.', exc_info=True)
        delete_service('sparkjob-' + job_id)
        delete_job_id(job_id)
        return jsonify({'error':'Failed to make pod.'}),500

    logger.info('Tracking ID %s', job_id)
    tracked = track(job_id)


    if 'Tracking' not in str(tracked):

        logger.error('Tracking failed on job id: %s', job_id)
        clean_up_pods(job_id)
        delete_job_id(job_id)

        return "failed to track"


    return job_id

if __name__ == "__main__":
    app.run(debug = True)

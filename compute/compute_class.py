#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import time,requests,json, sys, random, os, warnings, logging
from datetime import datetime
from flask import Flask, render_template, request, redirect,jsonify
from funcs import *
from jobClass import *
from auth import *
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


ARK_PREFIX = '99999'
MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')
TESTING = os.environ.get("NO_AUTH",False)

ORS_URL = os.environ.get("ORS_URL","ors.uvadco.io/")

app = Flask(__name__)

app.url_map.converters['everything'] = EverythingConverter

@app.route('/')
def homepage():

    logger.info('Homepage handling request %s', request)
    return "Status: Working"

@app.route('/job/<everything:ark>',methods = ['GET'])
@token_required
def job_status(ark):

    logger.info('Status request for ark: %s', ark)

    try:
        status =  get_job_status(ark,request.headers.get("Authorization"))
    except:
        logger.error('Error getting status of ark: %s',ark)
        return jsonify({'error':'Given ark either does not exist or is not a computation'}),400

    return jsonify({'Status':status})




@app.route('/job',methods = ['POST','GET'])
@token_required
def random_job():
    '''
    Runs script on given data using container of choice.
    {
        "datasetID":[],
        "scriptID":ark:99999/test,
        'containerID':ark:99999/sample-container
    }
    '''

    logger.info('Job endpoint handling request %s', request)

    if request.method == 'GET':

        running_pods = get_running_jobs()

        return jsonify({'runningJobIds':running_pods}),200

    #Creates job class from request
    job = Job(request,'custom', custom_container = True)

    if not job.correct_inputs:

        return jsonify({'error':job.error}),400


    minted = job.mint_job_id()

    if not minted:
        logger.error('Failed to mint identifier.')
        return jsonify({'error':'Minting Job Identifier failed'}),503

    #Creates Kubernetes Pod defition
    job.create_custom_k_defs()

    logger.info('Creating Pod %s', str(job.pod))
    try:

        job.create_pod()

    except:

        logger.error('Failed to create pod.', exc_info=True)
        job.delete_id()
        return jsonify({'error':'Failed to make pod.'}),500



    logger.info('Tracking ID %s', job.job_id)
    tracked = nitrack(job)
    #tracked = 'Tracking'

    if 'Tracking' not in str(tracked):

        logger.error('Tracking failed on job id: %s', job.job_id)
        job.delete_pod()
        job.delete_id()

        return "failed to track"


    return 'ark:' + job.namespace + '/' +job.job_id


@app.route('/nipype',methods = ['POST','GET'])
@token_required
def nipype_job():

    logger.info('Job endpoint handling request %s', request)


    job = Job(request,'nipype')

    if not job.correct_inputs:

        return jsonify({'error':job.error}),400


    minted = job.mint_job_id()

    if not minted:
        logger.error('Failed to mint identifier.')
        return jsonify({'error':'Minting Job Identifier failed'}),503


    job.create_nipype_defs()

    logger.info('Creating Pod %s', str(job.pod))
    try:

        job.create_pod()

    except:

        logger.error('Failed to create pod.', exc_info=True)
        job.delete_id()
        return jsonify({'error':'Failed to make pod.'}),500



    logger.info('Tracking ID %s', job.job_id)
    tracked = nitrack(job)

    if 'Tracking' not in str(tracked):

        logger.error('Tracking failed on job id: %s', job.job_id)
        job.delete_pod()
        job.delete_id()

        return "failed to track"


    return 'ark:' + job.namespace + '/' +job.job_id

@app.route('/spark',methods = ['POST','GET'])
@token_required
def compute():

    logger.info('Job endpoint handling request %s', request)

    if request.method == 'GET':

        running_pods = get_running_jobs()

        for pod in running_pods:
            pod = 'ark:' + ARK_PREFIX + '/' + pod

        return jsonify({'runningJobIds':running_pods}),200


    job = Job(request,'sparkjob')

    if not job.correct_inputs:

        return jsonify({'error':job.error}),400


    minted = job.mint_job_id()

    if not minted:
        logger.error('Failed to mint identifier.')
        return jsonify({'error':'Minting Job Identifier failed'}),503

    job.create_kubernetes_defs()

    logger.info('Creating Service %s', str(job.service))
    try:

        job.create_service()

    except:

        logger.error('Failed to create service.', exc_info=True)
        job.delete_id()
        return jsonify({'error':'Failed to make service.'}),500


    logger.info('Creating Pod %s', str(job.pod))
    try:

        job.create_pod()

    except:

        logger.error('Failed to create pod.', exc_info=True)
        job.delete_service()
        job.delete_id()
        return jsonify({'error':'Failed to make pod.'}),500



    logger.info('Tracking ID %s', job.job_id)
    tracked = track(job)

    if 'Tracking' not in str(tracked):

        logger.error('Tracking failed on job id: %s', job.job_id)
        job.delete_service()
        job.delete_pod()
        job.delete_id()

        return "failed to track"


    return 'ark:' + job.namespace + '/' +job.job_id

if __name__ == "__main__":
    if TESTING:
        app.config['TESTING'] = True
    app.run(host='0.0.0.0')

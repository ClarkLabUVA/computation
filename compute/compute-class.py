import time,requests,json, sys, random, os, warnings, logging
from datetime import datetime
from flask import Flask, render_template, request, redirect,jsonify
from funcs import *
from jobClass import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')

ORS_URL = os.environ.get("ORS_URL","ors.uvadco.io/")

app = Flask(__name__)

app.url_map.converters['everything'] = EverythingConverter

@app.route('/')
def homepage():

    logger.info('Homepage handling request %s', request)
    return "Status: Working"

@app.route('/job/<everything:ark>',methods = ['GET'])
def job_status(ark):

    logger.info('Status request for ark: %s', ark)

    try:
        status =  get_job_status(ark)
    except:
        logger.error('Error getting status of ark: %s',ark)
        return jsonify({'error':'Given ark either does not exist or is not a computation'}),400

    return jsonify({'Status':status})




@app.route('/job',methods = ['POST','GET'])
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

    #Creates job class from request
    job = Job(request,custom_container = True)

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
    tracked = nitrack(job.job_id,job.prefix)
    #tracked = 'Tracking'

    if 'Tracking' not in str(tracked):

        logger.error('Tracking failed on job id: %s', job.job_id)
        job.delete_pod()
        job.delete_id()

        return "failed to track"


    return job.job_id


@app.route('/nipype',methods = ['POST','GET'])
def nipype_job():

    logger.info('Job endpoint handling request %s', request)


    job = Job(request)

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
    tracked = nitrack(job.job_id,job.prefix)

    if 'Tracking' not in str(tracked):

        logger.error('Tracking failed on job id: %s', job.job_id)
        job.delete_pod()
        job.delete_id()

        return "failed to track"


    return job.job_id

@app.route('/spark',methods = ['POST','GET'])
def compute():

    logger.info('Job endpoint handling request %s', request)

    if request.method == 'GET':

        running_pods = get_running_jobs()

        return jsonify({'runningJobIds':running_pods}),200


    job = Job(request)

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
    tracked = track(job.job_id,job.prefix)

    if 'Tracking' not in str(tracked):

        logger.error('Tracking failed on job id: %s', job.job_id)
        job.delete_service()
        job.delete_pod()
        job.delete_id()

        return "failed to track"


    return job.job_id

if __name__ == "__main__":
    app.run(host='0.0.0.0')

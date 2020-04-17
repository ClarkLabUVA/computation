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

@app.route('/')
def homepage():

    logger.info('Homepage handling request %s', request)
    return "Status: Working"

@app.route('/job',methods = ['POST','GET'])
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
    tracked = track(job.job_id)

    if 'Tracking' not in str(tracked):

        logger.error('Tracking failed on job id: %s', job_id)
        job.delete_service()
        job.delete_pod()
        job.delete_id()

        return "failed to track"


    return job.job_id

if __name__ == "__main__":
    app.run(debug = True)

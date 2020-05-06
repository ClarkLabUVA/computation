import time,requests,json, sys, random, os, warnings, logging, threading
from datetime import datetime
from flask import Flask, render_template, request, redirect,jsonify
from funcs import *

MINIO_URL = os.environ.get('MINIO_URL','minionas.uvadcos.io/')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET = os.environ.get('MINIO_SECRET')
ORS_URL = os.environ.get("ORS_URL","ors.uvadco.io/")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    logger.info('Job endpoint handling request %s', request)

    valid, inputs = gather_inputs(request)
    track_id = inputs['job_id']

    full_id = 'ark:99999/' + track_id

    logger.info('Tracking Job ID: %s', track_id)
    exists = find_pod('sparkjob-' + track_id)

    if not exists:

        logger.error('Pod does not exsist for job : %s', track_id)
        return "No Pod"

    def track(track_id):

        logger.info('Thread following Job ID %s started.', track_id)

        while pod_running('sparkjob-' + track_id):
            logger.info('Tracking running Job ID %s.', track_id)
            time.sleep(30)

        logger.info('Job %s completed', track_id)
        job_status, logs = get_pod_logs('sparkjob-' + track_id)

        outputs = gather_job_outputs(track_id)
        output_ids, all_minted = mint_output_ids(outputs,job_id)

        if not all_minted:
            logger.error('Failed to mint all output ids for job ' %s.', track_id)

        logger.info('Updating Job ID: %s', track_id)
        success = update_job_id(track_id,job_status,logs)

        for output_id in output_ids:
            built = build_eg(track_id)
            if not built:
                logger.error('Failed to create eg for job %s',output_id)
                
        try:
            clean_up_pods(track_id)
        except:
            logger.error('Failed to clean up after job.', exc_info=True)


    thread = threading.Thread(target=track, kwargs={'track_id':track_id})
    thread.start()

    return "Tracking " + track_id

if __name__ == "__main__":
    app.run(port = 5001)

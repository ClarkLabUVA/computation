FROM jniestroy/nipy-runner

COPY [".", "/"]

COPY workflows.py /opt/miniconda-latest/envs/neuro/lib/python3.6/site-packages/nipype/pipeline/engine/

RUN chmod a+x /run_wf.sh

RUN bash -c 'source activate neuro'

CMD ["/bin/bash"]

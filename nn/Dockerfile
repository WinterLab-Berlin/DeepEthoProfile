# script to build the Docker image that will run the processing, using the base image created by Dockerfile_base
FROM ethoprofiler_nn_base_av

#copy code
ADD DataReaderAV.py /home/nn
ADD EthoCNN.py /home/nn
ADD mouse_v5.model /home/nn
ADD ProcComm.py /home/nn
ADD Logger.py /home/nn
ADD ProcessVideo.py /home/nn
ADD FrameSelect.py /home/nn

RUN mkdir /mnt/data && chown dep_user /mnt/data
USER dep_user

# Enable venv
#ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT python3 ProcComm.py







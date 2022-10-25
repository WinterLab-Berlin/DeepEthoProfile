# script to build the Docker image that will run the processing, using the base image created by Dockerfile_base
FROM ethoprofiler_nn_base_av

#copy code
ADD DataReaderAV.py /home/nn
ADD EthoCNN.py /home/nn
ADD mouse_v2.model /home/nn
ADD ProcComm.py /home/nn
ADD Logger.py /home/nn
ADD ProcessVideo.py /home/nn
ADD StackFrames.py /home/nn

ENTRYPOINT python3 ProcComm.py



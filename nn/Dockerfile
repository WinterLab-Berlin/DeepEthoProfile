FROM ethoprofiler_nn_base

#copy code
ADD DataReader.py /home/nn
ADD EthoCNN.py /home/nn
ADD mouse_v2.model /home/nn
ADD ProcComm.py /home/nn
ADD Logger.py /home/nn
ADD ProcessVideo.py /home/nn

ENTRYPOINT python3 ProcComm.py



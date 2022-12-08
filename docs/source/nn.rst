Processing module
=================

Main Processing
---------------

.. autoclass:: EthoCNN.EthoCNN(noClasses)
    :members:
    :undoc-members:
    :show-inheritance:
      
.. autoclass:: DataReaderAV.DataReaderAV
    :members:
    
Helper functions 
^^^^^^^^^^^^^^^^

Module **StackFrames** contains functions to prepare the video frames for the CNN input. 


.. autofunction:: StackFrames::getTestTensors(x)
.. autofunction:: StackFrames::getTensors(x, ann=None, modify=False)


Integration
-----------

.. autoclass:: ProcComm.ProcComm
    :members:
    :undoc-members:

.. autoclass:: ProcessVideo.ProcessVideo
    :members:
    :undoc-members:

.. autoclass:: Logger.Logger
    :members:
    :undoc-members:


Training and Testing
--------------------

.. autoclass:: TrainModel.TrainModel
    :members:
    :undoc-members:

.. autoclass:: TrainInterval.TrainInterval
    :members:
    :undoc-members:
   
.. autoclass:: TestModel.TestModel
    :members:
    :undoc-members:
   
.. autoclass:: TestInterval.TestInterval
    :members:
    :undoc-members:
   
   
SelectTrainingData

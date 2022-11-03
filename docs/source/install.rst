Installation
============


The current software version was tested on a Ubuntu 20.04 operating system. 

Hardware dependencies are: a CUDA 11.0 or better compatible graphic card with at least 4G of memory and at least 8G of system memory.

Software requirements are: NVidia CUDA driver, Docker, Python 3.8+, QT5 and python bindings. 


Copy the source files from the repository:

.. code-block::

   clone https://github.com/WinterLab-Berlin/DeepEthoProfile.git


Create the base Docker image:

.. code-block::

   sh DockerBase.sh 
   
This contains the all the libraies needed for the NN. 

Create the base Docker image:

.. code-block::

   sh Docker.sh 
   
Creates the Docker image that will perform the behaviour classification. 

If the trained model is not already present, it will be downloaded before creating the image.



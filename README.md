# DeepEthoProfile

Software to automatically annotate mouse behaviours inside a home cage.
The solution is based on a CNN that processes stacked frames and classifies first order behaviours

The system was tested to work on a computer running Ubuntu (20.04 or newer) with a NVidia(c) graphic card and CUDA(c) drivers installed. 
Other required software dependencies are: Docker(c) 20+, Python 3.8+, and PyQt 5+

## Instalation
git clone 

#### Create the Docker image containing the undelying framework 
sh DockerBase.sh

#### Create the Docker image for the processing software and download the trained model
sh Docker.sh

#### Start the application
sh EthoProfiler.sh


## Usage

#### Add Video 
- select a single video and offers the possibility to visualize it before adding it to the processing queue[Figure]
#### Add multiple videos 
- select multiple videos and add them to the processing queue [Figure]

The results will be saved at the location of the source video as a .CSV file. 
This file contains a header describing the significance of the numbers and a the software version used.
For each frame, there is number that corresponds to the automatically annotated behaviour (as defined in the header)


## File structure

#### Root folder
Contains the scripts for generating the Docker images and starting the application
Also here are the auxiliary software that were used to perform the video acquisition (Capture) and the manual anntotaion (VideoAnnotationViewer) 

#### nn folder
Contains all the processing, training and testing implementation.
The current version of the trained model will also be downloaded here. 
#### ui folder
Contains the files needed for the user interface

## Implementation details
A documentation of the source code can be found here: https://deepethoprofile.readthedocs.io

Read the paper [link] for more details.

## Training
The training was performed on a manual annotation database found here[link]

Training and testing on other videos can be performed using the TrainModel/TestModel files [describe the process?]


## License:
This project is licensed under the GNU General Public License v3.0. Note that the software is provided "as is", without warranty of any kind, express or implied. If you use the code or data, please cite us!


## Versions:
under development


## Acknowledgements:
Support for this work was received through the BMBF program “Alternatives to animal experiments”. 

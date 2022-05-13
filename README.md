# DeepEthoProfile

Software to automatically annotate mouse behaviours inside a home cage.
The solution is based on a CNN that processes stacked frames and classifies first order behaviours

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

#### nn folder
Contains all the processing, training and testing implementation
#### ui folder
Contains the files needed for the user interface

## Implementation details
(See paper for details)

## Training
The training was performed on a manual annotation database found here[link]

Training and testing on other videos can be performed using the TrainModel/TestModel files [describe the process?]

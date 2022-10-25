# creates the image containing the software environment needed for processing
docker build --tag ethoprofiler_nn_base_av -f ./nn/Dockerfile_base ./nn

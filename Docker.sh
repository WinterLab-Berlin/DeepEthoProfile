# creates a Docker image that will perform the processing

# as the NN model file is not present on the GitHub repository, it will be downloaded if it is not present
model_file=./nn/mouse_v5.model

if test -f "$model_file"; then
	echo "$model_file already present"
else
	#retrieve NN model
	curl -o "$model_file" "https://zenodo.org/records/14827053/files/mouse_v5.model?download=1"
fi

#create processing docker image
docker build --tag ethoprofiler_nn_av -f ./nn/Dockerfile ./nn

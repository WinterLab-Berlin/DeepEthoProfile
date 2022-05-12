model_file=./nn/mouse_v2.model

if test -f "$model_file"; then
	echo "$model_file already present"
else
	#retrieve NN model
	curl -o "$model_file" "https://zenodo.org/record/6382163/files/mouse_v2.model?download=1"
fi

#create processing docker image
docker build --tag ethoprofiler_nn -f ./nn/Dockerfile ./nn

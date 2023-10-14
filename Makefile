all: build tag push

NAME=k8s-llama2-gpu
VERSION=v1
REGISTRY="quay.io/rcarrata"
TOOL="docker"

build: 
	@${TOOL} build -t localhost/${NAME}:${VERSION} .
	
tag:
	@${TOOL} tag localhost/${NAME}:${VERSION} ${REGISTRY}/${NAME}:${VERSION}

push: 
	@${TOOL} push ${REGISTRY}/${NAME}:${VERSION}

run:
	@${TOOL} run -d -p 8080:8080 ${REGISTRY}/${NAME}:${VERSION}
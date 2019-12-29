IMG := ios-note
TAG := trial

font-setup:
	./script/setup.sh

docker-build:
	make -C py/

env:
	docker run -it --rm --init \
	--ipc host \
	--name ios-note \
	--volume `pwd`:/content \
	-w /content \
	${IMG}:${TAG} /bin/bash

.PHONY: build
build:
        docker build -t asterisk -f Dockerfile .

.PHONY: run
run:
        #docker run --name asterisk -d --rm --name asterisk --network=host asterisk || :
        docker run -v `pwd`/config:/etc/asterisk --name asterisk -d --rm --name asterisk --network=host asterisk || :

.PHONY: exec
exec:
        docker exec -it asterisk /bin/bash || :

.PHONY: stop
stop:
        docker stop asterisk || :

.PHONY: logs
logs:
        docker logs -f asterisk || :

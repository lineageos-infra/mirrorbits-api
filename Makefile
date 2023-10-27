.PHONY: update

build:
	docker build . -t mirrorbits-api
update: build
	-docker stop mirrorbits-api
	-docker rm mirrorbits-api
	docker run --restart always -v /data/mirror:/data/mirror --net=host --name mirrorbits-api -d mirrorbits-api:latest

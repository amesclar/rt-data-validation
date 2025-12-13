<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [python](#python)
	- [create requirements.txt](#create-requirementstxt)
- [docker](#docker)
	- [build image](#build-image)
	- [run image](#run-image)
	- [enter image](#enter-image)
	- [list running images](#list-running-images)
	- [prune all images](#prune-all-images)

<!-- /TOC -->
# python
## create requirements.txt
```
pip freeze > requirements.txt
```

# docker
## build image
```
sudo docker build -t rt-rt-data-validation .
```

## run image
```
sudo docker run -itv `pwd`:/app rt-rt-data-validation /bin/bash
```

## enter image
```
docker exec -it `docker ps | tail -n 1 | cut -c93-150` /bin/bash
```

based on
```
docker ps
CONTAINER ID   IMAGE                 COMMAND       CREATED         STATUS         PORTS     NAMES
a94191107776   rt-rt-data-validation   "/bin/bash"   3 minutes ago   Up 3 minutes             wonderful_nash
```

## list running images
```
docker ps
```

## prune all images
```
docker image prune -a
```

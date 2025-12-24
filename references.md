- [References](#references)
	- [Run](#run)
	- [Python](#python)
		- [Activate Virtual Environment](#activate-virtual-environment)
		- [Run Tests](#run-tests)
		- [Install Dependencies](#install-dependencies)
		- [Capture Dependencies](#capture-dependencies)
		- [Deactivate Virtual Environment](#deactivate-virtual-environment)
		- [Create Virtual Environment](#create-virtual-environment)
		- [Install venv](#install-venv)
		- [Install pip](#install-pip)
	- [Docker](#docker)
		- [Build image](#build-image)
		- [Run image](#run-image)
		- [Enter image](#enter-image)
		- [List running images](#list-running-images)
		- [Prune all images](#prune-all-images)

# References

## Run

```bash
python3 rt-data-validation.py --sut test_data/SUT-2025-12-19_10:59:49.log --test test_data/TEST-2025-12-19_10:59:49.log
```

## Python

### Activate Virtual Environment

```bash
source venv/bin/activate
```

### Run Tests
```
pytest test_validation.py
```

### Install Dependencies

```bash
pip install --no-cache-dir -r requirements.txt
```

### Capture Dependencies

```bash
pip freeze > requirements.txt
```

### Deactivate Virtual Environment

```bash
deactivate
```

### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Install venv

```bash
sudo apt update
sudo apt install python3-venv
```

### Install pip

```bash
sudo apt update
sudo apt install python3-pip
```

## Docker

### Build image

```bash
sudo docker build -t rt-rt-data-validation .
```

### Run image

```bash
sudo docker run -itv `pwd`:/app rt-rt-data-validation /bin/bash
```

### Enter image

```bash
docker exec -it `docker ps | tail -n 1 | cut -c93-150` /bin/bash
```

based on
```
docker ps
CONTAINER ID   IMAGE                 COMMAND       CREATED         STATUS         PORTS     NAMES
a94191107776   rt-rt-data-validation   "/bin/bash"   3 minutes ago   Up 3 minutes             wonderful_nash
```

### List running images

```bash
docker ps
```

### Prune all images

```bash
docker image prune -a
```

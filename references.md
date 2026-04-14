- [References](#references)
	- [Run](#run)
	- [Python](#python)
		- [Activate Virtual Environment](#activate-virtual-environment)
		- [Run Tests](#run-tests)
		- [Create Virtual Environment](#create-virtual-environment)
		- [Install Dependencies](#install-dependencies)
		- [Capture Dependencies](#capture-dependencies)
		- [Deactivate Virtual Environment](#deactivate-virtual-environment)
		- [Install venv](#install-venv)
		- [Install pip](#install-pip)

# References

## Run

```bash
source .venv/bin/activate
python3 rt_data_validation.py --dir logs
# python3 rt_data_validation.py --sut test_data/SUT-2026-03-25_09:54:06.log --test test_data/TEST-2026-03-25_09:54:06.log
# python3 rt_data_validation.py --sut test_data/SUT-2025-12-19_10:59:49.log --test test_data/TEST-2025-12-19_10:59:49.log
```

## Python

### Activate Virtual Environment

```bash
source .venv/bin/activate
```

### Run Tests
```
pytest test_validation.py
```

### Create Virtual Environment

```bash
python3 -m venv .venv
source venv/bin/activate
pip install -r requirements.txt
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

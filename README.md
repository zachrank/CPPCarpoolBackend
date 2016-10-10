# CPP Carpool backend
Python-flask backend for cpp carpool app. Server listens on port 8080.

### Requirements
 1. Python 2.7
 2. pip


### Setup
```
cd src
pip install -r requirements.txt
```

### Running the server
```
cd src
python server.py
```

### Docker w/ development
If you prefer to develop with docker, don't forget to forward port 8080

To build the container:
```
make build
```

And to run the container:
```
make dev
```

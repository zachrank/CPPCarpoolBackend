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

On Windows machines the Makefile needs to be modified in order to run. The path for the folder needs to be modified as below (the path needs to be specified per machine).

```
dev:
	docker run --rm -it -v c:/*insert path here*/cppcarpoolbackend/src:/usr/src/app -p 8080:8080 carpool-backend
```

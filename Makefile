build:
	docker build -t carpool-backend .

dev:
	docker run --rm -it -v `pwd`/src:/usr/src/app -p 8080:8080 carpool-backend

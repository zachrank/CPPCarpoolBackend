build:
	docker build -t carpool-backend .

net:
	docker network ls | grep cppcarpool || docker network create cppcarpool

dev: net
	docker run --rm -it --net cppcarpool -v `pwd`/src:/usr/src/app -p 8080:8080 carpool-backend

shell: net
	docker run --rm -it --net cppcarpool -v `pwd`/src:/usr/src/app -p 8080:8080 carpool-backend /bin/bash

test: net
	docker run --rm -it --net cppcarpool -v `pwd`/src:/usr/src/app -v `pwd`/tests:/usr/src/tests -p 8080:8090 carpool-backend /bin/bash -c "PYTHONPATH=\`pwd\` python ../tests/run_tests.py"

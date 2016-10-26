build:
	docker build -t carpool-backend .

dev:
	docker run --rm -it -v `pwd`/src:/usr/src/app -p 8080:8080 carpool-backend

shell:
	docker run --rm -it -v `pwd`/src:/usr/src/app -p 8080:8080 carpool-backend /bin/bash

test:
	docker run --rm -it -v `pwd`/src:/usr/src/app -v `pwd`/tests:/usr/src/tests -p 8080:8090 carpool-backend /bin/bash -c "PYTHONPATH=\`pwd\` python ../tests/run_tests.py"

.PHONY: test

clean:
	rm -rf openlyrics

install:
	python -m pipenv install

install/dev:
	python -m pipenv install --dev

openlyrics/clone:
	git clone https://github.com/openlyrics/openlyrics.git

openlyrics/port-to-python3:
	2to3 -w openlyrics/lib/python/openlyrics.py

test:
	cp .env.test .env
	python -m pipenv run python -m pytest test/unit -s

docker/build: clean openlyrics/clone openlyrics/port-to-python3
	docker build -t pyopenlp-convert -f docker/Dockerfile .

docker/run:
	docker run \
		-it \
		-d \
		-p 8000:8000 \
	  	pyopenlp-convert

# docker/run/daemon:
# 	docker run \
# 		-p 8000:8000 \
# 		-itd \
# 		--name pyopenlp-convert \
# 		pyopenlp-convert

flask/run:
	# there is probably a better way of doing this
	cp .env.flask .env
	cd openlp_convert && \
		PYTHONPATH=${PYTHONPATH}:../openlyrics/lib/python \
			python -m pipenv run python -m flask run

gunicorn/run:
	cp .env.gunicorn .env
	cd openlp_convert && \
		python -m pipenv run python -m gunicorn app:app

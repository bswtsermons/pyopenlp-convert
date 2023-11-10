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

docker/build:
	docker build -t pyopenlp-convert -f docker/Dockerfile .

docker/run:
	docker run -it pyopenlp-convert

docker/run/daemon:
	docker run \
		-p 5000:5000 \
		-itd \
		--name pyopenlp-convert \
		pyopenlp-convert

# flask/run:
# cd openlp_convert && \
#   FLASK_APP=hello \
#   FLASK_NOTES_DIR=notes \
#   FLASK_SESSION_TYPE=filesystem \
#   python -m pipenv run python -m flask run

flask/run:
	# there is probably a better way of doing this
	cp .env.flask .env
	cd openlp_convert && \
		PYTHONPATH=${PYTHONPATH}:../openlyrics/lib/python \
			python -m pipenv run python -m flask run

gunicorn/run:
	cp .env.flask .env
	cd openlp_convert && \
		python -m pipenv run python -m gunicorn app:app


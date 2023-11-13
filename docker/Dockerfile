FROM python:3.11.5
 
RUN pip install pipenv

ENV INSTALL_DIR /opt/pyopenlp_convert

RUN mkdir -p $INSTALL_DIR
# RUN mkdir -p $INSTALL_DIR/openlyrics/lib/

WORKDIR ${INSTALL_DIR}

COPY Makefile Pipfile Pipfile.lock ./

# install pipenv virtual env and fix openlyrics code
RUN make install
# RUN make openlyrics/clone openlyrics/port-to-python3

# need environment and entrypoint
COPY .env.docker .env.gunicorn
COPY docker/entrypoint.bash .

# install code
COPY openlp_convert/ ${INSTALL_DIR}/openlp_convert

# copy openlyrics code
COPY openlyrics/lib/python/openlyrics.py openlp_convert/ 

EXPOSE 8000

ENTRYPOINT [ "/bin/bash", "./entrypoint.bash" ]

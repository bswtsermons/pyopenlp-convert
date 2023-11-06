FROM python:3.11.5
 
RUN pip install pipenv

ENV INSTALL_DIR /opt/pyopenlp_convert

RUN mkdir -p $INSTALL_DIR
# RUN mkdir -p $INSTALL_DIR/openlyrics/lib/

COPY Makefile ${INSTALL_DIR}
COPY Pipfile ${INSTALL_DIR}
COPY Pipfile.lock ${INSTALL_DIR}
COPY docker/entrypoint.bash ${INSTALL_DIR}
COPY openlp_convert/ ${INSTALL_DIR}/openlp_convert
# COPY openlyrics/lib/python/openlyrics.py $INSTALL_DIR/openlyrics/lib/python/openlyrics.py 

WORKDIR ${INSTALL_DIR}

# should have everything we need.  get the code running
RUN make install
RUN make openlyrics/clone openlyrics/port-to-python3

EXPOSE 5000

ENTRYPOINT [ "/bin/bash", "./entrypoint.bash" ]

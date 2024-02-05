FROM python:slim-bullseye

# Install gdal
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY bin/* /usr/local/bin
RUN chmod 755 /usr/local/bin/*

RUN mkdir /process
COPY ./process/* /process

# The S3 KEY/SECRET are dummy one generated from local minio server
ENV PROCESS_API_ENDPOINT=http://host.docker.internal:5252/oapi-p\
    S3_HOST=http://host.docker.internal:9001\
    S3_BUCKET=process\
    S3_KEY=xxxxx\
    S3_SECRET=yyyyy

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

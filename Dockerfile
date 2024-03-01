FROM python:3.13.0a4-slim

# prepare base image
RUN apt update && apt install --yes \
    locales \
    locales-all \
    entr \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# prepare application folder
RUN mkdir -p /app/src

# install python dependencies
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Fix file watcher on Mac (see: https://github.com/eradman/entr/issues/3)
ENV ENTR_INOTIFY_WORKAROUND 1

# prepare application container
COPY entrypoint /app/
ENTRYPOINT ["/app/entrypoint"]
COPY ./src /app/src

EXPOSE 8000
ENV SERVICE_PORT=8000

ARG VERSION=local  # override at build
ENV VERSION=${VERSION}

CMD ["start"]

VOLUME [ "/app/src" ]
VOLUME [ "/app/data/db.sqlite3" ]


FROM python:3-bookworm

RUN bash -euo pipefail <<EOF
# prepare base image
apt update
apt install --yes --no-install-recommends \
    locales \
    locales-all \
    entr \
    git \
    wkhtmltopdf
rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

# prepare application folder
mkdir -p /app/src /app/shared
EOF

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
CMD ["start"]

VOLUME [ "/app/src" ]
VOLUME [ "/app/shared" ]
VOLUME [ "/app/htmlcov" ]

# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster
COPY ./ /app
WORKDIR /app

RUN apt-get update && apt-get -y install gcc python3-dev

RUN ./build.sh
# tidalrr should be installed in /app/dist/tidalrr

CMD ["/app/dist/tidalrr"]
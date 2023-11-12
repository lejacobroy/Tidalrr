# syntax=docker/dockerfile:1

FROM python:3.11

WORKDIR /app
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt update && apt upgrade -y && apt install ffmpeg -y

ENTRYPOINT ["python3"]

CMD ["app.py"]
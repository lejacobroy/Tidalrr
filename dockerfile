# syntax=docker/dockerfile:1

FROM python:3.11

WORKDIR /app
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3"]

CMD ["app.py"]
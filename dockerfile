# syntax=docker/dockerfile:1

FROM python:3.11

WORKDIR /app
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN git clone https://github.com/willowmck/plexPlaylistImporter.git PPI
RUN pip install --no-cache-dir -r PPI/requirements.txt

COPY . .

ENTRYPOINT ["python3"]

CMD ["app.py"]
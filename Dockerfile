FROM python:3.12-alpine

ENV PYTHONUNBUFFERED 1
ENV TZ="America/New_York"

USER root

RUN mkdir -p /app
COPY . /app

WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
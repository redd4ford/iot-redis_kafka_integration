FROM    python:3.9-alpine
ENV PYTHONUNBUFFERED 1

ADD     . /api
WORKDIR /api
RUN     pip3 install -r requirements.txt
CMD     ["python", "manage.py", "runserver"]

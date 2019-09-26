FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /dlptooling
WORKDIR /dlptooling
COPY requirements.txt /dlptooling/
RUN pip install -r requirements.txt
COPY . /code/
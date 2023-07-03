FROM python:3.8-slim-buster

RUN apt-get update && apt-get install git zip --assume-yes

RUN mkdir -p webapp
WORKDIR webapp

# Add these earlier to allow for optimizations
ADD requirements.txt .
RUN pip install -r requirements.txt

# Add the rest of the files
COPY . .

ENTRYPOINT flask run --host=0.0.0.0
FROM python:3.11-slim-buster

RUN apt-get update && apt-get install git zip --assume-yes

RUN mkdir -p pwncrates
WORKDIR pwncrates

# Add these earlier to allow for optimizations
# Gunicorn is only needed for prod, so we don't include it in the requirements
RUN pip install gunicorn
ADD requirements.txt .
RUN pip install -r requirements.txt

# Add the rest of the files
COPY . .

WORKDIR /
ENTRYPOINT gunicorn --workers 4 'pwncrates:app' --chdir pwncrates -b 0.0.0.0 --log-level info
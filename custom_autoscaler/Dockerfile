FROM custompodautoscaler/python:latest
# Install dependencies for debugging
RUN apt-get update
RUN apt-get install jq curl -y
# Set up aliases for easy debugging
RUN echo 'alias metrics="curl -X GET http://localhost:5000/api/v1/metrics | jq ."' >> ~/.bashrc
RUN echo 'alias evaluation="curl -X POST http://localhost:5000/api/v1/evaluation | jq ."' >> ~/.bashrc
# Add in python requirements to install dependencies
ADD requirements.txt /
# Install dependencies, done before adding Py files to allow Docker to cache better
RUN pip install -r /requirements.txt
# Add config, evaluator and metric gathering Py scripts
ADD config.yaml evaluate.py metric.py /
FROM python:3

WORKDIR /usr/src/app

RUN apt-get update && apt-get install nano

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "bash", "./keep_running.sh" ]
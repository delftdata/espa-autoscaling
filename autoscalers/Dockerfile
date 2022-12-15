FROM python:3

WORKDIR /usr/src/app

RUN apt-get update && apt-get install nano

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

COPY . .

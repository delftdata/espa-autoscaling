FROM python:3

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y vim curl

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

COPY . .

RUN cargo run --release --bin policy -- --topo examples/offline/flink_wordcount_topology.csv --rates examples/offline/flink_rates.log --system flink


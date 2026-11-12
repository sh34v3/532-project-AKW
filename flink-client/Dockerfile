
# we need to use jammy specifically for a dumb reason.

# python:3.11-slim (and other versions) are NOT shipped with access to 
# package repositories that hold openjdk-17-jdk. Furthermore, eclipse-temurin:17
# does not ship with access to package repositories that hold python3.10 or python3.11

# I don't want to add some random PPA. For some reason, 
# eclipse-temurin Jammy (Ubuntu 22.04 LTS) does have access to a repo that holds
# the python version we need.

# I don't know enough about apt (or linux package repos in general) to really say much
# but this was stupid to debug.

#FROM eclipse-temurin:17-jdk-jammy
FROM eclipse-temurin:11-jdk-jammy

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl 

WORKDIR /usr/src/app

COPY flink-connector-rabbitmq-3.0.1-1.17.jar /opt/connectors/flink-connector-rabbitmq.jar
RUN curl -fsSL -o /opt/connectors/amqp-client.jar \
    https://repo1.maven.org/maven2/com/rabbitmq/amqp-client/5.17.0/amqp-client-5.17.0.jar
COPY requirements.txt .

RUN pip install --no-cache-dir  -r requirements.txt

COPY . .

CMD python3 ./src/main.py

# Builds Proctor Docker Image

# Use Alpine Linux
FROM alpine:latest
MAINTAINER puopoloj1@wit.edu
USER root

# Install SDKs and utilities
RUN apk update
RUN apk add openjdk8 python3 vim git

# Copy Python source to container
WORKDIR /home/proctor
COPY README.md .
COPY *.py ./

# Install Proctor deps
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy JUnit 4.x libs
WORKDIR /home/proctor/lib
COPY ./lib/junit4.jar .
COPY ./lib/hamcrest-core-1.3.jar .

# Copy basic Configuration file to default root dir
WORKDIR /root
COPY ./basic.cfg ./.proctor.cfg

# Make a working dir
RUN mkdir /home/proctor/work

# Set up ENV variables
ENV PATH "$PATH:/usr/lib/jvm/java-1.8-openjdk/bin"

# Run when container starts
WORKDIR /home/proctor
ENTRYPOINT ["ash"]





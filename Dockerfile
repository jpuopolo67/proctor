# Builds Proctor Docker Image

# Use Alpine Linux
FROM alpine:latest
MAINTAINER puopoloj1@wit.edu
USER root

# Install SDKs and utilities
RUN apk update
RUN apk add openjdk8 python3 vim git

# Copy JUnit 4.x libs
WORKDIR /home/proctor/lib
COPY ./lib/junit4.jar .
COPY ./lib/hamcrest-core-1.3.jar .

# Copy Python source to container and run deps
WORKDIR /home/proctor
COPY README.md .
COPY *.py ./
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Make proctor.py a runnable app
RUN chmod +x proctor.py

# Make a working dir
WORKDIR /home/proctor/work

# Create a basic config file that the user can edit
WORKDIR /root
COPY ./basic.cfg ./.proctor.cfg

# Create a volume so that user can save config file edits
VOLUME /data

# Set up ENV variables so that we can find the Java tools
ENV PATH "$PATH:home/proctor:/usr/lib/jvm/java-1.8-openjdk/bin"

# Run when container starts
WORKDIR /home/proctor
ENTRYPOINT ["ash"]





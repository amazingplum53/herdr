FROM python:3.12

ENV BASEDIR="/workspace" 
ENV PROJECT_NAME="drf_template" 

WORKDIR $BASEDIR/$PROJECT_NAME

RUN echo "$BASEDIR/$PROJECT_NAME" > /usr/local/lib/python3.12/site-packages/project-path.pth

COPY dev.requirements.txt /tmp/dev.requirements.txt

RUN apt-get update

RUN apt-get install -y curl git docker.io docker-compose awscli less make npm nodejs jq

RUN curl -fsSL https://get.pulumi.com | sh

ENV PATH="/root/.pulumi/bin:${PATH}"

# Verify packages are installed correctly
RUN git --version && pip --version && docker --version && pulumi version && aws --version 

RUN pip install uv

RUN uv pip install -r /tmp/dev.requirements.txt --system


FROM python:3.12-slim

ENV BASEDIR="/server" 
ENV PROJECT_NAME="drf_template" 

RUN mkdir -p $BASEDIR $BASEDIR/$PROJECT_NAME

WORKDIR $BASEDIR/$PROJECT_NAME

RUN echo "$BASEDIR/$PROJECT_NAME" > /usr/local/lib/python3.12/site-packages/project-path.pth

COPY . .

RUN pip install uv

RUN uv pip install -r .devcontainer/server.requirements.txt --system

#HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
#CMD curl -f http://localhost:8000/ || exit 1

CMD python "django_api/uvicorn_server.py"


